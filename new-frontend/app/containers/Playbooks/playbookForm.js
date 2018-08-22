import React, { PureComponent } from 'react';
import {  AvForm, AvGroup } from 'availity-reactstrap-validation';
import Field from 'components/Input/field';
import Input from 'components/Input';
import T from 'prop-types';
import FullHeightCard from 'components/FullHeightCard';
import { CardTitle, CardBody, CardSubtitle, CardText, Label, FormGroup, FormText, Button } from 'reactstrap';


export default class PlaybookForm extends PureComponent {
  static propTypes =
    {
      book: T.object.isRequired,
      onSubmit: T.func.isRequired,
    };

  constructor(props)
  {
    super(props);

    this.state = Object.assign(...Object.entries(props.book.variables).map(([k, v]) => (
      {[k]:v.value})));

    this.onInputTextChange = this.onInputTextChange.bind(this);
    this.generateField = this.generateField.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
  }
  onInputTextChange(e) {
    console.log("Text change: ",e.target.name,  e.target.value);
    const form = this.state;
    form[e.target.name] = e.target.value;
    this.setState(form);
  }
  onSubmit(e)
  {
    e.preventDefault();
    this.props.onSubmit(this.state);
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
          <AvForm onValidSubmit={this.onSubmit}>
            {
              Object.entries(book.variables).map(([k,v]) => this.generateField(k, v))
            }
            <Button primary type="submit" block>
              Play
            </Button>
          </AvForm>
        </CardText>
      </CardBody>
    </FullHeightCard>);
  }
  generateField(id, field) {
    const fieldValue = this.state[id];
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
          return (<option key={k} value={k}>{v.description}</option>);
        })}
        </Field>

      )
    }
  }
};
