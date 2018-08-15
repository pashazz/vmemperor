import React, {PureComponent} from 'react';
import {Button, Card, CardBody, CardFooter, CardText, CardTitle, Col, Row, Table, Collapse, UncontrolledAlert, ButtonGroup} from 'reactstrap';
import NextTable from 'react-bootstrap-table-next';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faCheck from '@fortawesome/fontawesome-free-solid/faCheck';
import {sizeFormatter} from "../../../utils/sizeFormatter";
import StorageAttach from "./storageAttach";
import {detachvdi, vdilist} from "../../../api/vdi";
import isolist from "../../../api/isolist";

import ControlledTable, { selectors } from 'containers/ControlledTable';
import {connect} from 'react-redux';
import { compose } from 'redux';
import { createStructuredSelector } from 'reselect';
const checkBoxFormatter = (cell, row) =>
{
  if (cell)
  {
    return (
      <span>
        { cell && (<FontAwesomeIcon icon={faCheck}/>)}
      </span>
    )
  }
};


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


class Storage extends PureComponent {
  constructor(props)
  {
    super(props);
    this.state = {
      vdiAttach: false,
      isoAttach: false,
      selected: [],
      refreshWidgets: false,
    };
    this.toggleVdiAttach = this.toggleVdiAttach.bind(this);
    this.toggleIsoAttach = this.toggleIsoAttach.bind(this);
    this.onDetach = this.onDetach.bind(this);
    this.refreshWidgets = this.refreshWidgets.bind(this);
  }

  refreshWidgets()
  {
    this.setState({refreshWidgets: !this.state.refreshWidgets})
  }
  onDetach()
  {
    for (const ref of this.props.table_selection)
    {
      console.log("diskInfo: ", this.props.diskInfo);
      console.log("key:", ref);
      const vdi = this.props.diskInfo.filter(row => {console.log("row.key=", row.key, "ref=", ref); return  row.key === ref})[0]['VDI'];
      this.props.onDetachVdi(vdi);
    }
    this.refreshWidgets();
  }
  toggleIsoAttach()
  {
    let set = {
      isoAttach: !this.state.isoAttach,
    };
    if (set.isoAttach)
      set.vdiAttach = false;
    this.setState(
      set
    );
  }
  toggleVdiAttach()
  {
    let set = {
      vdiAttach: !this.state.vdiAttach,
    };
    if (set.vdiAttach)
      set.isoAttach = false;
    this.setState(
      set
    );
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

    const selectRow = {
      mode: 'checkbox',
      clickToSelect: true,
      selected: this.state.selected,
      onSelect: (row, isSelect) => {
        console.log(isSelect);
        console.log(this.state);
        if (isSelect) {
          this.setState(() => ({
            selected: [...this.state.selected, row.key]
          }));
        }
        else {
          this.setState(() => ({
            selected: this.state.selected.filter(x => x !== row.key),
          }))
        }
      },
      onSelectAll: (isSelect, rows) => {
        if (isSelect) {
        this.setState(() => ({
          selected: rows.map(r => r.key)
        }));
        }
        else {
          this.setState(() => ({
            selected: [],
          }))
        }
      }
};
    const detachDisabled = this.props.table_selection.length === 0;
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
              <Button size="lg" color="danger" disabled={detachDisabled} onClick={this.onDetach}> Detach </Button>
              <Collapse id="collVdi"
                isOpen={this.state.vdiAttach}>
                <UncontrolledAlert color='info'>Double-click to attach a disk. You can't delete an attached disk</UncontrolledAlert>
              <StorageAttach
                  uuid={this.props.data.get('uuid')}
                  caption="Hard disks"
                  fetch={this.props.requestVdi}
                  data={this.props.vdiList}
                  refresh={this.state.refreshWidgets}
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
                  refresh={this.state.refreshWidgets}
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
