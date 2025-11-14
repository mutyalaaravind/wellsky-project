import React, {
  cloneElement,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";
import { useDebouncedCallback } from "use-debounce";
import { type MedicationsApiHook } from "./useMedicationsApi";
import SearchMedicationInput, {
  SearchMedicationInputProps,
} from "screens/review/SearchMedicationInput";

type CachedSearchDict = {
  [key: string]: any[];
};

const cachedSearches: CachedSearchDict = {};

type useSearchMedicationParams = {
  searchMedications: MedicationsApiHook["searchMedications"];
};

export type useSearchMedicationReturn = {
  searchRef: React.RefObject<HTMLInputElement>;
  debounceSearch: ReturnType<typeof useDebouncedCallback>;
  renderSearchInput: (
    props?: Partial<SearchMedicationInputProps>,
  ) => JSX.Element;
  suggestions: any[];
  error: string | null;
  setSearchValue: React.Dispatch<React.SetStateAction<string>>;
  clearSuggestions: () => void;
};

function useSearchMedication({
  searchMedications,
}: useSearchMedicationParams): useSearchMedicationReturn {
  const [searchValue, setSearchValue] = useState("");
  const [completionBusy, setCompletionBusy] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const controller = useRef<AbortController>();

  const clearSuggestions = useCallback(() => {
    setSuggestions([]);
    setError(null);
  }, []);

  const debounceSearch = useDebouncedCallback((value: string) => {
    if (!value?.trim()) {
      setCompletionBusy(false);
      setSuggestions([]);
      setError(null);
      controller.current?.abort("Aborting ongloing request.");
      return;
    }
    setCompletionBusy(true);
    let promise;
    if (cachedSearches[value]) {
      promise = Promise.resolve(cachedSearches[value]);
      controller.current?.abort("Aborting ongloing request.");
    } else {
      // abort any existing call before putting new one.
      controller.current?.abort("Aborting ongloing request.");
      controller.current = new AbortController();
      const signal = controller.current.signal;

      promise = searchMedications(value, signal);
    }

    promise
      .then((results) => {
        setSuggestions(results);
        setCompletionBusy(false);
        cachedSearches[value] = results;
        if (results.length) {
          setError(null);
        } else {
          setError(
            "No Search found. Please try editing search term or mark Unlisted.",
          );
        }
      })
      .catch((error) => {
        if (error === "Aborting ongloing request.") {
          return;
        }
        setSuggestions([]);
        setCompletionBusy(false);
        console.error("Error searching medications:", error);
        setError(error.toString());
      });
  }, 350);

  const searchRef = useRef<any>();

  const clearSearch = useCallback(() => {
    setSuggestions([]);
    controller.current?.abort("Aborting ongloing request.");
    setCompletionBusy(false);
    setSearchValue("");
  }, []);

  const searchInput = useMemo(() => {
    return (
      <SearchMedicationInput
        setSearchValue={setSearchValue}
        searchValue={searchValue}
        clearSearch={clearSearch}
        searchRef={searchRef}
        completionBusy={completionBusy}
        debounceSearch={debounceSearch}
      />
    );
  }, [clearSearch, completionBusy, debounceSearch, searchValue]);

  const renderSearchInput = useCallback(
    (props?: Partial<SearchMedicationInputProps>) => {
      return cloneElement(searchInput, props);
    },
    [searchInput],
  );

  return {
    searchRef,
    debounceSearch,
    renderSearchInput,
    suggestions,
    error,
    setSearchValue,
    clearSuggestions,
  };
}

export default useSearchMedication;
