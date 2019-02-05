import React, {PureComponent}  from 'react';
import T from 'prop-types';
import IPT from 'react-immutable-proptypes';
import Select from 'react-select';
import {FormGroup, Label, Col} from 'reactstrap';


class ISO extends PureComponent {
  state = {
    options: [],
  };

  static getDerivedStateFromProps(props, state)
  {
    return { options:  props.isos.map((iso) => {
        return {
          value: iso.uuid,
          label: iso.name_label
        };
      }),
    };
  }

  static PropTypes = {
    isos: IPT.listOf(IPT.record),
    onChange: T.func.isRequired,
  };

  render() {
    return (
      <div>
            <Select options={this.state.options}
                    placeholder="Select ISO Image..."
                    onChange={this.props.onChange}
                    isSearchable name="iso" id="iso"
                    required
            />
      </div>
    )
  }
}

export default ISO;
