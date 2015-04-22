import React from 'react';
import Modal from './modal.jsx';

class VMForm extends React.Component {
  render() {
    return (
      <form role="form" id="create-vm-form">
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-servers"></i></span>
          <select className="form-control input" id="pool-select" name="pool-select">
              <option value="--">Select where to deploy instance</option>
              <option value="https://172.31.0.14:443/">Pool A</option>
              <option value="https://172.31.0.32:443/">Pool Z</option>
          </select>
        </div>
        <br />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-ubuntu"></i></span>
          <select className="form-control" id="template-select" name="template-select" enabled>
              <option value="--">Select OS template for your virtual machine</option>
          </select>
        </div>
        <hr />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-address"></i></span>
          <input  type="text"
                  className="form-control"
                  placeholder="Your full name (e.g. John Smith)"
                  id="user-fullname"
                  name="user-fullname"
                  enabled />
        </div>
        <br />
        <div className="row">
          <div className="col-sm-12 col-lg-12">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-user"></i></span>
              <input  type="text"
                      className="form-control"
                      placeholder="Your login for new VM"
                      id="username"
                      name="username"
                      enabled />
              <span className="input-group-addon"><i className="icon-at"></i></span>
              <input  type="text"
                  className="form-control"
                  placeholder="Choose hostname for your VM"
                  id="hostname"
                  name="hostname"
                  enabled />
              <span className="input-group-addon">.at.ispras.ru</span>
            </div>
          </div>
        </div>
        <br />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-password"></i></span>
          <input  type="password"
                  className="form-control input"
                  placeholder="Choose password for your VM"
                  id="password"
                  name="password"
                  enabled />
          <span className="input-group-addon"><i className="icon-password"></i></span>
          <input  type="password"
                  className="form-control input"
                  placeholder="Confirm password"
                  id="password2"
                  name="password2"
                  enabled />
        </div>
        <br />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-noteslist" style={{ fontSize: '28px' }}></i></span>
          <textarea
                  type="text"
                  className="form-control input"
                  placeholder="What do you want to do with this virtual machine?"
                  id="vm-description"
                  name="vm-description"
                  style={{resize: 'vertical'}}
                  enabled />
        </div>
        <br />
        <h4>Resources settings</h4>
        <div className="row">

          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-processorthree"></i></span>
              <input type="number" pattern="\d*"
                      className="form-control" id="vcpus" name="vcpus" defaultValue="1" enabled />
              <span className="input-group-addon">cores</span>
            </div>
          </div>

          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-ram"></i></span>
              <input type="number" pattern="\d*"
                     className="form-control" id="ram" name="ram" defaultValue="256" enabled />
              <span className="input-group-addon">MB</span>
            </div>
          </div>

          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-hdd"></i></span>
              <input type="number" pattern="\d*"
                     className="form-control" id="hdd" name="hdd" defaultValue="9" enabled />
              <span className="input-group-addon">GB</span>
            </div>
          </div>
        </div>
        <br />
        <h4>HTTP/HTTPS reverse-proxy settings</h4>
        <div className="row">

          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-network">:80</i></span>
              <input type="number" pattern="\d*"
                     className="form-control input"
                     id="redirection-http"
                     name="redirection-http"
                     defaultValue="80"
                     enabled />
            </div>
          </div>
          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-network">:8080</i></span>
              <input type="textnumber" pattern="\d*"
                     className="form-control input"
                     id="redirection-http-alt"
                     name="redirection-http-alt"
                     defaultValue="8080"
                     enabled />
            </div>
          </div>
          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-network">:443</i></span>
              <input type="number" pattern="\d*"
                     className="form-control input"
                     id="redirection-ssl"
                     name="redirection-ssl"
                     defaultValue="443"
                     enabled />
            </div>
          </div>
        </div>
        <br />
        <button className="btn btn-lg btn-primary btn-block" id="create-button" enabled>Create VM</button>
      </form>
    );
  }
}

class CreateVM extends React.Component {
  constructor() {
    super();
    this.showModal = this.showModal.bind(this);
    this.hideModal = this.hideModal.bind(this);
    this.renderModal = this.renderModal.bind(this);

    this.state = { modalShow: false };
  }

  showModal() {
    this.setState({ modalShow: true });
  }

  hideModal() {
    this.setState({ modalShow: false });
  }

  renderModal() {
    return this.state.modalShow ?
      <Modal title="Virtual machine options" show lg close={this.hideModal}>
        <VMForm />
      </Modal> :
      null;
  }

  render () {
    return (
      <div>
        <a onClick={this.showModal}>CreateVM</a>
        {this.renderModal()}
      </div>
    );
  }
};

export default CreateVM;
