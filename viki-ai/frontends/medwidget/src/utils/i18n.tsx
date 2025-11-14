export const pluralize = (count: number, singular: string, plural: string) => {
  return count === 1 ? singular : plural;
};

export const capitalizeWords = (str: string) => {
  const result = str.replace(/([A-Z])/g, " $1");
  return result.charAt(0).toUpperCase() + result.slice(1);
};
