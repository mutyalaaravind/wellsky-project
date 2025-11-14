import { produce } from "immer";
import React, { ReactNode, createContext, useReducer } from "react";

export interface SearchContextType {
  search: string;
  searchValue: string;
  selectedTags: string[]; // Add the selectedTags property
  identifier: string;
}

const initialState: SearchContextType = {
  search: "",
  selectedTags: [], // Add the selectedTags property
  searchValue: "", // Add the searchValue property
  identifier: "",
};

const initialContextValue = {
  state: initialState,
};

export const SearchContext = createContext<{
  state: SearchContextType;
  dispatch?: React.Dispatch<SearchContextAction>;
}>(initialContextValue);

export const useSearchContext = () => {
  const context = React.useContext(SearchContext);
  if (context === undefined) {
    throw new Error(
      "useSearchContext must be used within a SearchContextProvider",
    );
  }
  return context;
};

interface SearchContextAction {
  type:
    | "setSearch"
    | "setSearchResults"
    | "setSearchLoading"
    | "setSelectedTags"
    | "addSelectedTags"
    | "removeSelectedTags"
    | "setSearchValue"
    | "setIdentifier";
  payload: any;
}

export const SearchContextProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [state, dispatch] = useReducer(
    (state: SearchContextType, action: SearchContextAction) => {
      switch (action.type) {
        case "setSearch":
          return produce(state, (draft) => {
            draft.search = action.payload;
          });
        case "setSearchValue":
          return produce(state, (draft) => {
            draft.searchValue = action.payload;
          });
        case "setSelectedTags":
          return produce(state, (draft) => {
            draft.selectedTags = action.payload;
          });
        case "addSelectedTags": // Add the addSelectedTags case
          return produce(state, (draft) => {
            // tags should be unique so we don't add the same tag twice
            if (draft.selectedTags.includes(action.payload)) {
              return;
            }
            draft.selectedTags.push(action.payload);
          });
        case "removeSelectedTags": // Add the removeSelectedTags case
          return produce(state, (draft) => {
            draft.selectedTags = draft.selectedTags.filter(
              (tag) => tag !== action.payload,
            );
          });
        case "setIdentifier":
          return produce(state, (draft) => {
            draft.identifier = action.payload;
          });
        default:
          return state;
      }
    },
    initialState,
  );

  return (
    <SearchContext.Provider
      value={{
        state,
        dispatch,
      }}
    >
      {children}
    </SearchContext.Provider>
  );
};
