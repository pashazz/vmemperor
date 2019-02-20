/**
 *
 * Playbooks
 *
 */

import React, {useCallback, useState} from 'react';
//import IPT from 'react-immutable-proptypes';
//import { FormattedMessage } from 'react-intl';
//import reducer from './reducer';
//import saga from './saga';
//import messages from './messages';
import {ButtonDropdown, DropdownToggle, DropdownMenu, DropdownItem} from 'reactstrap';
import PlaybookForm from "./playbookForm";
import {executePlaybook} from "./actions";
import {CreateVm, PlaybookList} from "../../generated-models";
import {useQuery} from "react-apollo-hooks";
import Variables = CreateVm.Variables;

interface Props {
  vms: string[]
}


const Playbooks = ({vms}: Props) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [currentId, setCurrentId] = useState<number | null>(null);
  const toggle = useCallback(() => setDropdownOpen(!dropdownOpen), [dropdownOpen]);
  const {data} = useQuery<PlaybookList.Query, PlaybookList.Variables>(PlaybookList.Document);
  const pbks = data.playbooks;

  console.log("Current playbook ID", currentId);
  return (
    <div>
      <ButtonDropdown size="lg" isOpen={dropdownOpen} toggle={toggle}>
        <DropdownToggle
          size="lg"
          caret>
          Playbooks
        </DropdownToggle>
        <DropdownMenu>
          {
            pbks.map((playbook, index) => {
                return (
                  <DropdownItem
                    key={index}
                    id={playbook.id}
                    onClick={() => setCurrentId(index)}
                  >
                    {playbook.name}
                  </DropdownItem>);
              }
            )
          }
        </DropdownMenu>
      </ButtonDropdown>
      {
        currentId !== null && (
          <PlaybookForm
            book={pbks[currentId]}
            vms={vms}
          />)
      }
    </div>);
};

export default Playbooks;
