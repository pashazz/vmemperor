import {useMemo} from "react";
import {object, string} from "yup";

export const useReactSelectFromRecord = <T extends ListItem>(dataSource: T[],
                                                      labelFunction: (item: T) => string = null,
                                                      filterFunction: (item: T) => boolean = null) => {
  if (!labelFunction) { // Default is using nameLabel
    labelFunction = (item: T) => item.nameLabel || item.nameDescription || `No name (UUID: ${item.uuid})`;
  }
  if (!filterFunction)
    filterFunction = (item) => true;

  const valueFunction = (item: T) => item.uuid;

  return useMemo(() => dataSource.filter(filterFunction).map((item): Option => (
      {
        value: valueFunction(item),
        label: labelFunction(item),
      }
    )
  ), [dataSource, labelFunction, filterFunction]);
};

export interface Option {
  value: string,
  label: string,
}

export const OptionShape = () => object().shape<Option>({
    value: string().required(),
    label: string().required(),
  }
);

interface ListItem {
  nameLabel?: string,
  nameDescription?: string,
  uuid: string,
}
