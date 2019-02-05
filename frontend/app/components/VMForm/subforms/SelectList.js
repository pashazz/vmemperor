import React, {PureComponent}  from 'react';
import T from 'prop-types';
import IPT from 'react-immutable-proptypes';
import Select from 'components/Select';
//import AvSelect from '@availity/reactstrap-validation-select';
import {FormGroup, Label, Col} from 'reactstrap';


class SelectList extends PureComponent {
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

  static propTypes = {
    data: IPT.listOf(IPT.record).isRequired,
    onChange: T.func.isRequired,

  };

  render() {
    const {data, ...props} = this.props;
    return (
      <div style={{flex: 1}}>
        <Select options={this.state.options}
                {...props} />
      </div>
    )
  }
}

export default SelectList;
