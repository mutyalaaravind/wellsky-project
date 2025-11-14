import { message } from "antd";
import { useEffect } from "react";
import { convertToNestedObject } from "../utils/helpers";
import ReactDOM from "react-dom/client";
import { ChakraProvider, IconButton, Tooltip } from "@chakra-ui/react";
import React from "react";
import { EditOutlined, RobotOutlined } from "@ant-design/icons";

function useCustomFormWrapper(form: any, newData: any, mount: any, onEvidenceRequested?: (field: any) => void) {
  useEffect(() => {
    const listener = (e: any) => {
      //message.success(`field ${e?.detail.id} Clicked`);
      console.log("fieldLabelClicked", e?.detail);
      onEvidenceRequested?.(e?.detail);
    };
    window.addEventListener("fieldLabelClicked", listener);
    return () => window.removeEventListener("fieldLabelClicked", listener);
  }, []);

  useEffect(() => {
    if (form && newData) {
      console.log({ "hook": "useCustomFormWrapper", form, newData, mount });
      const shadowRootElement = document.getElementById(mount)?.shadowRoot;

      // According to events, Highlighting fields.
      const eventListeners = [] as [
        HTMLElement,
        keyof HTMLElementEventMap,
        (...args: any[]) => void,
      ][];
      const roots = [] as ReactDOM.Root[];
      if (shadowRootElement) {
        const keys = Object.keys(newData);

        for (const k of keys) {
          const pathedName = k.split(".");

          const controllerId = pathedName.join("_");

          const fieldController =
            shadowRootElement.getElementById(controllerId);
          const fieldContainer = shadowRootElement.getElementById(k);

          const label = fieldContainer?.querySelector(
            `label[for="${controllerId}"]`,
          ) as HTMLLabelElement;

          if (label) {
            console.log("label", label);
            const listener = () => {
              window.dispatchEvent(
                new CustomEvent("fieldLabelClicked", { detail: { id: k, text: label.innerText } }),
              );
            };
            label.addEventListener("click", listener);

            eventListeners.push([label, "click", listener]);
          }

          // Handling for radio
          if (fieldController?.querySelectorAll('input[type="radio"]').length) {
            const nearestParent = fieldController?.querySelectorAll(
              `input[type="radio"][value="${newData[k]}"]`,
            )?.[0]?.parentElement;

            if (nearestParent) {
              nearestParent.style.border = "2px solid orange";
              nearestParent.style.borderRadius = "50%";
            }

            const formValueObj = convertToNestedObject({
              [k]: {
                radioValues: JSON.stringify(newData[k]),
              },
            });

            form.setFieldsValue(formValueObj);
            continue;
          }
          // Handling for radio ends here

          // Handling for Checkbox
          if (
            fieldController?.querySelectorAll('input[type="checkbox"]').length
          ) {
            let values: any[] = [];
            if (Array.isArray(newData[k])) {
              values = [...newData[k]];
            } else {
              values = [newData[k]];
            }

            for (const val of values) {
              const checkbox = fieldController?.querySelectorAll(
                `input[type="checkbox"][value="${val}"]`,
              )?.[0] as HTMLInputElement;

              const nearestParent = checkbox?.parentElement;

              if (nearestParent) {
                nearestParent.style.border = "2px solid #edaf3d";
                nearestParent.style.borderRadius = "4px";

                if (checkbox) {
                  const listener = (e: any) => {
                    const checked = e.target.checked;
                    const aiValueChecked = values.includes(e.target.value);

                    if (checked === aiValueChecked) {
                      nearestParent.style.border = "2px solid #edaf3d";
                    } else {
                      nearestParent.style.border = "2px solid #8b8bf3";
                    }
                  };
                  checkbox.addEventListener("change", listener);
                  eventListeners.push([checkbox, "change", listener]);
                }
              }
            }

            const formValueObj = convertToNestedObject({
              [k]: {
                checkboxValues: JSON.stringify(newData[k]),
              },
            });

            form.setFieldsValue(formValueObj);
            continue;
          }
          // Handling for Checkbox ends here

          let portal = document.createElement("div");
          if (fieldContainer && fieldContainer.querySelector(".ant-row")) {
            portal.id = "portal_" + k;
            portal.style.display = "none";
            const fieldRow = fieldContainer.querySelector(".ant-row");
            fieldRow?.appendChild(portal);
          }

          const registerPortal = (
            portal: HTMLDivElement,
            afterValueChange: (isAiValue: boolean) => void,
          ) => {
            const reactRoot = ReactDOM.createRoot(portal);
            reactRoot.render(
              <ChakraProvider>
                <div
                  style={{
                    display: "flex",
                    marginTop: 10,
                    gap: 4,
                  }}
                >
                  {/* <Tooltip
                    placement="bottom"
                    label={<div>Click to use original value</div>}
                  >
                    <IconButton
                      borderRadius={0}
                      borderWidth={0}
                      aria-label="Using previous value"
                      bgColor="zest.400"
                      color={"#FFFFFF"}
                      borderColor={"zest.400"}
                      onClick={() => {
                        afterValueChange(false);
                        portal.style.display = "block";
                      }}
                    >
                      <EditOutlined
                        style={{
                          color: "blue",
                        }}
                      />
                    </IconButton>
                  </Tooltip> */}
                  <Tooltip
                    placement="bottom"
                    label={<div>Click to use AI value</div>}
                  >
                    <IconButton
                      borderRadius={0}
                      borderWidth={0}
                      aria-label="Using AI value"
                      bgColor="zest.400"
                      color={"#FFFFFF"}
                      borderColor={"zest.400"}
                      onClick={() => {
                        const formValueObj = convertToNestedObject({
                          [k]: newData[k],
                        });

                        form.setFieldsValue(formValueObj);
                        afterValueChange(true);
                        portal.style.display = "none";
                      }}
                    >
                      <RobotOutlined
                        style={{
                          color: "blue",
                        }}
                      />
                    </IconButton>
                  </Tooltip>
                </div>
              </ChakraProvider>,
            );
            roots.push(reactRoot);
          };

          // For other select fields
          if (fieldController?.getAttribute("type") === "search") {
            const nearestParent = fieldController.closest(
              ".ant-select-selector",
            ) as HTMLElement;

            if (nearestParent) {
              nearestParent.style.borderBottom = "2px solid #edaf3d";

              if (fieldContainer) {
                registerPortal(portal, (isAi) => {
                  if (isAi) {
                    nearestParent.style.borderBottom = "2px solid #edaf3d";
                  } else {
                    nearestParent.style.borderBottom = "2px solid #8b8bf3";
                  }
                });
                const observer = new MutationObserver(
                  (mutationList, observer) => {
                    for (const mutation of mutationList) {
                      if (mutation.type === "childList") {
                        const newValue = form.getFieldValue(pathedName);
                        let valueChanged = false;
                        if (Array.isArray(newData[k])) {
                          if (Array.isArray(newValue)) {
                            valueChanged =
                              newValue.every((v) => newData[k].includes(v)) &&
                              newValue.length === newData[k].length;
                          }
                        } else if (newValue !== newData[k]) {
                          valueChanged = true;
                        }

                        if (valueChanged) {
                          nearestParent.style.borderBottom =
                            "2px solid #8b8bf3";
                          portal.style.display = "block";
                        } else {
                          nearestParent.style.borderBottom =
                            "2px solid #edaf3d";
                          portal.style.display = "none";
                        }
                      }
                    }
                  },
                );

                observer.observe(fieldContainer, {
                  childList: true,
                  subtree: true,
                });
              }
            }

            const formValueObj = convertToNestedObject({
              [k]: newData[k],
            });

            form.setFieldsValue(formValueObj);
            continue;
          }

          // For other text fields
          if (
            fieldController?.getAttribute("type") === "text" ||
            fieldController instanceof HTMLTextAreaElement
          ) {
            // ant-select-selection-search-input
            // const input = fieldController?.querySelectorAll('input')[0]
            const nearestParent = fieldController;

            if (nearestParent) {
              nearestParent.style.borderBottom = "2px solid #edaf3d";

              registerPortal(portal, (isAi) => {
                if (isAi) {
                  nearestParent.style.borderBottom = "2px solid #edaf3d";
                } else {
                  nearestParent.style.borderBottom = "2px solid #8b8bf3";
                }
              });

              const listener = (e: any) => {
                if (e.target.value === newData[k]) {
                  nearestParent.style.borderBottom = "2px solid #edaf3d";
                  portal.style.display = "none";
                } else {
                  nearestParent.style.borderBottom = "2px solid #8b8bf3";
                  portal.style.display = "block";
                }
              };
              fieldController.addEventListener("keyup", listener);
              eventListeners.push([fieldController, "keyup", listener]);
            }

            const formValueObj = convertToNestedObject({
              [k]: newData[k],
            });

            form.setFieldsValue(formValueObj);
            continue;
          }
        }

        return () => {
          eventListeners.forEach(([element, type, listener]) =>
            element.removeEventListener(type, listener),
          );
          roots.forEach((root) => root.unmount());
        };
      }
    }
  }, [form, newData, mount]);
}

export default useCustomFormWrapper;
