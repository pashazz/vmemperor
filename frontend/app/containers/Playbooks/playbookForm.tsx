import React, { PureComponent } from 'react';
import {  AvForm, AvGroup } from 'availity-reactstrap-validation';
import Field from '../../components/Input/field';
import Input from '../../components/Input';
import T from 'prop-types';
import FullHeightCard from '../../components/FullHeightCard';
import { CardTitle, CardBody, CardSubtitle, CardText, Label, FormGroup, FormText, Button } from 'reactstrap';
import {PlaybookList, PlaybookLaunch} from "../../generated-models";
import {booleanLiteral} from "babel-types";




interface Props {
  book : PlaybookList.Playbooks
  vms : string[]
}

type VariableList = Record<string, string | number | boolean> | null;

type OriginalVariableList = Record<string, VariableDescription>;

interface State {
  variables : VariableList
  originalVariables: OriginalVariableList
}



export default class PlaybookForm extends PureComponent<Props, State> {
  constructor(props)
  {
    super(props);

    let variables : OriginalVariableList | null = null;
    if (props.book.variables)
    {
      variables = JSON.parse(props.book.variables);
      // @ts-ignore
      let stateVariables : VariableList =  Object.assign(...Object.entries(variables).map(([k, v]) => (
      {[k]:v.value})));


      this.state = {
        variables: stateVariables,
        originalVariables: variables
      }
    }


    this.onInputTextChange = this.onInputTextChange.bind(this);
    this.generateField = this.generateField.bind(this);
  }
  onInputTextChange(e) {
    console.log("Text change: ",e.target.name,  e.target.value);
    const form = this.state;
    form.variables[e.target.name] = e.target.value;
    this.setState(form);
  }
  render()
  {
    const { book } = this.props;
    return (
    <FullHeightCard>
      <CardBody>
      <CardTitle>{book.name}</CardTitle>
        <CardSubtitle>{book.description}</CardSubtitle>
        <CardText>
          <PlaybookLaunch.Component>
            {
              (trigger, {data, loading, error}) =>
              {
                if (data)
                {
                  console.log("Data obtained: ", data);
                }
                if (loading)
                {
                  console.log("Loading:", loading);
                }
                if (error)
                {
                  console.log("Error: ", error);
                }
                let onSubmit = (e : Event) =>
                {
                  e.preventDefault();
                  trigger(
                    {
                      variables: {
                        id: book.id,
                        vms: this.props.vms,
                        variables: JSON.stringify(this.state.variables)
                      }
                    }
                  );
                };
                return (
                  <AvForm onValidSubmit={onSubmit}>
                    {
                      Object.entries(this.state.originalVariables).map(
                        ([k,v]) => this.generateField(k, v))
                    }
                    <Button primary type="submit" block>
                      Play
                    </Button>
                  </AvForm>
                );
              }
            }
          </PlaybookLaunch.Component>
        </CardText>
      </CardBody>
    </FullHeightCard>);
  }
  generateField(id, field : VariableDescription) {
    const fieldValue = this.state.variables[id];
    let fieldType = null;
    switch (field.type) {
      case 'str': // field type ""
        fieldType = 'text';
        break;
      case 'int':
        fieldType = 'number';
        break;

    }
    let label = null;
    let multiple = false;
    if (field.type === 'option' && field.multiple) {
      multiple = true;
    }

    if (field.description) {
      label = field.description;
    }
    else {
      label = id;
    }

    if (fieldType) {
      return (<Field
        onChange={this.onInputTextChange}
        key={id}
        id={id}
        name={id}
        label={label}
        type={fieldType}
        multiple={multiple}
        value={fieldValue}
        helpMessage={id}
        required
      />)

    }
    else if (field.type === 'bool')
    {
      return (
        <FormGroup>
        <AvGroup check>
          <Label check>
            <Input
              onChange={this.onInputTextChange}
              key={id}
              type="checkbox"
              name={id}
              id={id}
            />
            {label}
          </Label>
          <FormText>{id}</FormText>
        </AvGroup>
        </FormGroup>
        );
    }
    else if (field.type === 'option')
    {
      return (
        <Field type="select"
               onChange={this.onInputTextChange}
               key={id}
               name={id}
               id={id}
               helpMessage={id}
               multiple={multiple}
               label={label}

        >
          {Object.entries(field.options).map(([k, v]) => {
            let value = v.value;
            if (typeof value === 'boolean')
              value = value.toString();
            return (<option key={k} value={value}>{v.description}</option>);
        })}
        </Field>
      )
    }
  }
};
