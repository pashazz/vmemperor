import React, {PureComponent} from 'react';
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardText,
  CardTitle,
  Col,
  Collapse,
  Row,
  UncontrolledAlert
} from 'reactstrap';
import {sizeFormatter} from "../../../utils/formatters";
import StorageAttach from "./storageAttach";
import {detachvdi} from "../../../api/vdi";

import ControlledTable, {ColumnType, selectors} from '../../../containers/ControlledTable';
import {connect} from 'react-redux';
import {compose} from 'redux';
import {createStructuredSelector} from 'reselect';
import {checkBoxFormatter} from "../../../utils/formatters";
import {VmInfo} from "../../../generated-models";
import Vm = VmInfo.Vm;



const columns = [
  {
    dataField: 'device',
    text: 'Name'

  },
  {
    dataField: 'type',
    text: 'Type',

  },
  {
    dataField: 'name_label',
    text: 'Disk name',

  },

  {
    dataField: 'virtual_size',
    text: 'Size',
    formatter: sizeFormatter,
  },
  {
    dataField: 'attached',
    text: 'Attached',
    formatter: checkBoxFormatter,
  },

  {
    dataField: 'bootable',
    text: 'Bootable',
    formatter: checkBoxFormatter,
  },


];

interface InjectedProps {
  table_selection: string[],
}

interface Props extends InjectedProps
{
  vm : Vm
}

interface State {
  vdiAttach: boolean, //If user attaches a VDI
  isoAttach: boolean, // If user attaches an ISO
  detachDisabled: boolean,
}

class Storage extends PureComponent<Props, State> {
  constructor(props)
  {
    super(props);
    this.state = {
      vdiAttach: false,
      isoAttach: false,

      detachDisabled: false,
    };
    this.toggleVdiAttach = this.toggleVdiAttach.bind(this);
    this.toggleIsoAttach = this.toggleIsoAttach.bind(this);
    this.onDetach = this.onDetach.bind(this);

  }

  onDetach()
  {
    for (const ref of this.props.table_selection)
    {
      const vdi = this.props.vm.disks.filter(row => {return  row.id === ref})[0].VDI.uuid;
      this.props.onDetachVdi(vdi);
    }

  }
  toggleIsoAttach()
  {
    let set : Partial<State> = {
      isoAttach: !this.state.isoAttach,
    };
    if (set.isoAttach)
      set.vdiAttach = false;
    this.setState(
      set as State
    );
  }
  toggleVdiAttach()
  {
    let set : Partial<State> = {
      vdiAttach: !this.state.vdiAttach,
    };
    if (set.vdiAttach)
      set.isoAttach = false;
    this.setState(
      set as State
    );
  }

  static getDerivedStateFromProps(props, state)
  {
    if (!props.table_selection)
      return state;
     return {
       ...state,
       detachDisabled: props.table_selection.length === 0
     }
  }
  render()
  {
    const actions = [
      {
        text: "Create",
        color: "info",
        type: "always",
        handler: () => { console.log("EMIT Create new Disk!")}

      },
      {
        text: "Delete",
        color: "danger",
        type: "selection",
        handler: (row) => { console.log ("Delete a Disk!", row); },
        filter: (row) => {return row.VMs.length === 0;}
      }

    ];



    const DiskTable = ControlledTable("disks");

    return (
      <React.Fragment>

      <Row>
        <Col sm={12}>
          <Card>
            <CardBody>
              <CardTitle>Virtual disks</CardTitle>
              <CardText>
                <DiskTable
                  columns={columns}
                  data={this.props.diskInfo}
                  keyField="key"
                  />
              </CardText>
            </CardBody>
            <CardFooter>
              <Button size="lg" color="success" onClick={this.toggleVdiAttach} active={this.state.vdiAttach} aria-pressed="true"> Attach virtual hard disk </Button>
              <Button size="lg" color="success" onClick={this.toggleIsoAttach} active={this.state.isoAttach} aria-pressed="true"> Attach ISO image </Button>
              <Button size="lg" color="danger" disabled={this.state.detachDisabled} onClick={this.onDetach}> Detach </Button>
              <Collapse id="collVdi"
                isOpen={this.state.vdiAttach}>
                <UncontrolledAlert color='info'>Double-click to attach a disk. You can't delete an attached disk</UncontrolledAlert>
              <StorageAttach
                  uuid={this.props.data.get('uuid')}
                  caption="Hard disks"
                  fetch={this.props.requestVdi}
                  data={this.props.vdiList}
                  showConnectedTo
                  onAttach={this.props.onAttachVdi}
                  actions={actions}
                  />
              </Collapse>
              <Collapse id="collIso"
                        isOpen={this.state.isoAttach}>
                <UncontrolledAlert color='info'>Double-click to attach an ISO</UncontrolledAlert>
                <StorageAttach
                  uuid={this.props.data.get('uuid')}
                  caption="ISO images"
                  fetch={this.props.requestIso}
                  data={this.props.isoList}
                  showConnectedTo={false}
                  onAttach={this.props.onAttachIso}
                />
              </Collapse>

            </CardFooter>
          </Card>

        </Col>
      </Row>
      </React.Fragment>
    );
  }
}

const mapStateToProps = createStructuredSelector({
  table_selection: selectors("disks").makeSelectionSelector()
});
const mapDispatchToProps = {};
const withConnect = connect(mapStateToProps, mapDispatchToProps);

export default compose(withConnect)(Storage);
