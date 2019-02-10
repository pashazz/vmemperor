/**
*
* Vmform
*
*/
import React from 'react';
import T from 'prop-types';
import autofill from  'react-autofill-innerref';
import { FormattedMessage } from 'react-intl';
import messages from './messages';
import styles from './styles.css';
import VMInput from './helpers';


import { AvForm } from 'availity-reactstrap-validation';


import Pool from "./subforms/Pool";
import { FormContainer } from 'ez-react-form';

interface FormValues {
  pool :string;
  template : string;
  storage: string;
}

const initialValues : FormValues = {
  pool: '',
  template: '',
  storage: ''
};

interface FormProps<Values> {
  formikBag : FormikProps<Values>
};


const VMForm : React.FunctionComponent = () => {
  return (
    <FormContainer>

    </FormContainer>
};


export default VMForm;
