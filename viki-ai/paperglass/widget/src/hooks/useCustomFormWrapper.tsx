import { message } from "antd";
import { useEffect, useRef } from "react";
import { convertToNestedObject } from "../utils/helpers";
import ReactDOM from "react-dom/client";
import { ChakraProvider, IconButton, Tooltip } from "@chakra-ui/react";
import React from "react";
import { EditOutlined, RobotOutlined } from "@ant-design/icons";

function useCustomFormWrapper(
  form: any,
  newData: any,
  mount: any,
  onEvidenceRequested?: (field: any, newData: any) => void,
) {
  let labelToRemoveStyles = useRef<HTMLLabelElement | null | undefined>(null);
  useEffect(() => {
    const listener = (e: any) => {
      //message.success(`field ${e?.detail.id} Clicked`);
      console.log("fieldLabelClicked", e?.detail);
      onEvidenceRequested?.(e?.detail, newData);
    };
    window.addEventListener("fieldLabelClicked", listener);
    return () => window.removeEventListener("fieldLabelClicked", listener);
  }, [onEvidenceRequested, newData]);

  useEffect(() => {
    // According to events, Highlighting fields.
    const eventListeners = [] as [
      HTMLElement,
      keyof HTMLElementEventMap,
      (...args: any[]) => void,
    ][];
    // const labelsToRemoveStyles = [] as HTMLLabelElement[];
    console.log("useCustomFormWrapper", form, newData, mount);
    const shadowRootElement = document.getElementById(mount)?.shadowRoot;

    const innerMountElement = shadowRootElement?.getElementById(mount);

    const newDatakeyMaps: any = newData
      ? Object.keys(newData)
          .map((k) => {
            const pathedName = k.split(".");

            const controllerId = pathedName.join("_");

            return {
              [controllerId]: { key: k, value: newData[k] },
            };
          })
          .reduce((prev, next) => {
            return { ...prev, ...next };
          }, {})
      : ({} as any);
    console.log("newDatakeyMaps", newDatakeyMaps);

    if (innerMountElement) {
      const mainListener = (e: Event) => {
        if ((e.target as HTMLElement).tagName === "SPAN") {
          const nearestLabel = (e.target as HTMLElement).closest("label");

          const key = nearestLabel?.getAttribute("for");
          console.log("labelKey", key);
          //console.log("nearestLabel", nearestLabel,key,newDatakeyMaps);
          let resolvedKey = null;
          let fieldPath;
          let resolvedValue;
          resolvedKey = Object.keys(newDatakeyMaps).find((k) => k === key);
          console.log("resolvedKey", resolvedKey);
          if (!resolvedKey) {
            resolvedKey = Object.keys(newDatakeyMaps).find((k) =>
              key?.includes(k),
            );

            if (resolvedKey) {
              const resolvedKeyPathFlat = resolvedKey.split(".").join("_");
              const fieldPathArray = key
                ?.replace(resolvedKeyPathFlat, "")
                ?.split("_")
                ?.filter((k) => k);
              const [first, ...rest] = fieldPathArray || [];
              fieldPath = [first, (rest || []).join("_")].join(".");

              resolvedValue = newDatakeyMaps[resolvedKey].value;

              for (const iterator of fieldPath?.split(".") || []) {
                const object: any = resolvedValue;
                if (object && typeof object === "object") {
                  resolvedValue = object[iterator];
                } else {
                  resolvedValue = null;
                  break;
                }
              }
            }
          }
          console.log("nearestLabel", nearestLabel, key, resolvedKey);
          if (nearestLabel && resolvedKey && newDatakeyMaps[resolvedKey]) {
            nearestLabel.style.transition = "background-color 2s";
            nearestLabel.style.backgroundColor = "#e1c94bb5";
            nearestLabel.style.borderRadius = "4px";

            if (
              labelToRemoveStyles.current &&
              labelToRemoveStyles.current !== nearestLabel
            ) {
              labelToRemoveStyles.current.style.backgroundColor = "";
              labelToRemoveStyles.current.style.borderRadius = "";
            }

            labelToRemoveStyles.current = nearestLabel;
            window.dispatchEvent(
              new CustomEvent("fieldLabelClicked", {
                detail: {
                  id: newDatakeyMaps[resolvedKey].key,
                  text: nearestLabel?.innerText,
                  path: nearestLabel.dataset.pathedName,
                  fieldPath,
                  resolvedValue,
                  value: nearestLabel.dataset.value,
                  actualKey: key,
                },
              }) as Event,
            );
          }
        }
      };
      innerMountElement.addEventListener("click", mainListener);
      eventListeners.push([innerMountElement, "click", mainListener]);
    }

    console.log("innerMountElement", innerMountElement);

    try {
      // Remove the ant-affix-menu

      const menu = shadowRootElement?.querySelector(".ant-affix-menu");
      const menuParent = menu?.parentElement;
      const fieldsContainer = menuParent?.nextSibling;
      (fieldsContainer as HTMLElement)?.classList?.remove("ant-col-20");
      (fieldsContainer as HTMLElement)?.classList?.add("ant-col-24");
      menuParent?.remove();
    } catch (error) {}
    if (form && newData) {
      console.log({ hook: "useCustomFormWrapper", form, newData, mount });

      const roots = [] as ReactDOM.Root[];
      if (shadowRootElement) {
        const keys = Object.keys(newData);

        for (const k of keys) {
          if (newData[k] === undefined || newData[k] === null) {
            continue;
          }
          const pathedName = k.split(".");

          const controllerId = pathedName.join("_");

          const fieldController =
            shadowRootElement.getElementById(controllerId);
          const fieldContainer = shadowRootElement.getElementById(k);
          //console.log("fieldController", fieldController);
          const label = fieldContainer?.querySelector(
            `label[for="${controllerId}"]`,
          ) as HTMLLabelElement;

          // let labelToRemoveStyles: HTMLLabelElement | undefined;

          if (label) {
            console.log("label", label);
            label.dataset.pathedName = pathedName.join(".");
            /*
            const listener = () => {
              window.dispatchEvent(
                new CustomEvent("fieldLabelClicked", {
                  detail: { id: k, text: label.innerText },
                }) as Event,
              );
              try {
                // eslint-disable-next-line @typescript-eslint/no-this-alias
                label.style.transition = "background-color 2s";
                label.style.backgroundColor = "#e1c94bb5";
                label.style.borderRadius = "4px";

                if (
                  labelToRemoveStyles.current &&
                  labelToRemoveStyles.current !== label
                ) {
                  labelToRemoveStyles.current.style.backgroundColor = "";
                  labelToRemoveStyles.current.style.borderRadius = "";
                }

                labelToRemoveStyles.current = label;

                // setTimeout(() => {
                //   label.style.backgroundColor = "";
                //   setTimeout(() => {
                //     label.style.borderRadius = "";
                //   }, 2000);
                // }, 2000);
              } catch (error) {
                console.log("error in label click", error);
              }
            };
            label.addEventListener("click", listener);
            eventListeners.push([label, "click", listener]);
            */
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
            console.log("radioValues", k, JSON.stringify(newData[k]));
            const formValueObj = convertToNestedObject({
              [k]: {
                radioValues: newData[k],
              },
            });

            form.setFieldsValue(formValueObj);
            if (label) {
              label.dataset.value = JSON.stringify(newData[k]);
            }
            continue;
          }
          // Handling for radio ends here

          // Handling for Checkbox
          if (
            fieldController?.querySelectorAll('input[type="checkbox"]').length
          ) {
            console.log("checkbox", fieldController);
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
            console.log("text control", k, newData[k]);
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

          //for date time
          console.log(
            "fieldContainer datetime check",
            fieldContainer,
            fieldContainer?.constructor.name,
          );
          if (fieldContainer instanceof HTMLDivElement) {
            console.log("span", fieldContainer.querySelectorAll("input"));
            if (fieldContainer.querySelectorAll("input").length) {
              const nearestParent = fieldContainer.querySelectorAll("input")[0];
              console.log("nearestParent", nearestParent);
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
                nearestParent.addEventListener("keyup", listener);
                eventListeners.push([nearestParent, "keyup", listener]);
              }

              const formValueObj = convertToNestedObject({
                [k]: newData[k],
              });

              form.setFieldsValue(formValueObj);
              continue;
            }
          }

          if (Array.isArray(newData[k])) {
            console.log("array", newData[k]);
            const formValueObj = convertToNestedObject({
              [k]: newData[k],
            });

            form.setFieldsValue(formValueObj);
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
