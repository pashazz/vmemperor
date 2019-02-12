import React from 'react';
import T from 'prop-types';
import { InputGroup, InputGroupAddon,  InputGroupText } from 'reactstrap';
import SelectList from './SelectList';
import {AvGroup, AvFeedback} from 'availity-reactstrap-validation';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCompactDisc} from "@fortawesome/free-solid-svg-icons";
import {useQuery} from "react-apollo-hooks";
import {TemplateList} from "../../../generated-models";

function Template({onChange }) {
  const {data : {templates}}  = useQuery<TemplateList.Query>(TemplateList.Document);

  if (templates.length === 0) {
    return null;
  }

   return (
     <AvGroup>
    <InputGroup style={ {padding: '10px'}}>
      <InputGroupAddon addonType="prepend">
        <InputGroupText>
          <FontAwesomeIcon icon={faCompactDisc}/>
        </InputGroupText>
      </InputGroupAddon>
    <SelectList
      style={{flex: 1}}
      data={templates}
      onChange={onChange}
      placeholder="Select Template..."
      name="template"
      id="template"
      required
    />
      <AvFeedback>Select a template to use as configuration basis</AvFeedback>
    </InputGroup>
     </AvGroup>
  );
}


export default Template;
