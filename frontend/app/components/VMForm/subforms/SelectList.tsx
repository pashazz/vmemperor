import React, {PureComponent, useMemo} from 'react';
import T from 'prop-types';
import IPT from 'react-immutable-proptypes';
import Select from '../../../components/Select';
//import AvSelect from '@availity/reactstrap-validation-select';
import {FormGroup, Label, Col} from 'reactstrap';
import {AvSelectProps} from "@availity/reactstrap-validation-select/AvSelect";
import {JSXAttribute} from "babel-types";


/*class SelectList extends PureComponent {
  state = {
    options: [],
  };

  static getDerivedStateFromProps(props, state)
  {
    return { options:  props.data.map((item) => {
        return {
          value: item.uuid,
          label: item.name_label
        };
      }).toArray(),
    };
  }

*/
type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
interface Value {
  uuid: string;
  nameLabel: string;
}

interface DataProps {
  data: Value[];
}
type HTMLSelect = React.HTMLProps<HTMLSelectElement>;
type Props = DataProps & AvSelectProps & Omit<HTMLSelect, "data">;



const SelectList = ({data, ...props} : Props)  => {
  const options = useMemo(() => data.map((item: Value) => (
    {
      value : item.uuid,
      label: item.nameLabel,
    })), [data]);

    return (
      <div style={{flex: 1}}>
        <Select options={options}
                {...props as AvSelectProps} />
      </div>
    )
  };


export default SelectList;
