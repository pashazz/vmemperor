import {useMemo} from "react";
import {FormikPropsValues, FormContext, Values} from "./props";
import {Form, Field} from "formik";
import {
  faDatabase,
  faHdd,
  faMemory,
  faMicrochip,
  faServer,
  faSignature,
  faTag
} from "@fortawesome/free-solid-svg-icons";
import Select from '../Select';
import {
  IsoList,
  NetworkList,
  PoolList,
  SrContentType,
  StorageList,
  StorageListFragment,
  TemplateList
} from "../../generated-models";
import formatBytes from "../../utils/sizeUtils";
import {useQuery} from "react-apollo-hooks";
import {useReactSelectFromRecord} from "../../hooks/form";
import messages from "./messages";
import React from "react";
import {FormattedMessage} from "react-intl";
import Input from '../Input';
import {faComment} from "@fortawesome/free-solid-svg-icons/faComment";
import {faUser} from "@fortawesome/free-solid-svg-icons/faUser";
import {faKey} from "@fortawesome/free-solid-svg-icons/faKey";
import {Button} from "reactstrap";
import CheckBoxComponent from "../Checkbox";
import {networkTypeOptions} from "./props";
import {faDesktop} from "@fortawesome/free-solid-svg-icons/faDesktop";
import styled from "styled-components";

const H4 = styled.h4`
margin: 20px;
`;

const VMForm = (props: FormikPropsValues) => {
  const {data: {pools}} = useQuery<PoolList.Query>(PoolList.Document);
  const poolOptions = useReactSelectFromRecord(pools);

  const {data: {templates}} = useQuery<TemplateList.Query>(TemplateList.Document);
  const templateOptions = useReactSelectFromRecord(templates);

  const {data: srData} = useQuery<StorageList.Query>(StorageList.Document);
  const srs = useMemo(() => srData.srs.filter(
    sr => sr.contentType === SrContentType.User &&
      !sr.PBDs.every(pbd => !pbd.currentlyAttached)), [srData])
  const srOptions = useReactSelectFromRecord(srs, (item: StorageListFragment.Fragment) => {
    return `${item.nameLabel} (${formatBytes(item.spaceAvailable, 2)} available)`
  });

  const {data: {networks}} = useQuery<NetworkList.Query>(NetworkList.Document);
  const networkOptions = useReactSelectFromRecord(networks);

  const {data: isoData} = useQuery<IsoList.Query>(IsoList.Document);
  const isos = useMemo(() => isoData.isos.filter(iso =>
    !iso.SR.isToolsSr && !iso.SR.PBDs.every(pbd => !pbd.currentlyAttached)),
    [isoData]);
  const isoOptions = useReactSelectFromRecord(isos);

  console.log("Errors:", props.errors);
  console.log("Values:", props.values);
  const currentTemplateOsKind = useMemo(() => {
    if (!props.values.template)
      return null;

    return templates.filter(t => t.uuid === props.values.template.value)[0].osKind;
  }, [props.values.template]);
  return (
    <FormContext.Provider value={props}>
      <Form>
        <H4><FormattedMessage {...messages.infrastructure} /></H4>
        <Field name="pool"
               component={Select}
               options={poolOptions}
               placeholder="Select a pool to install on..."
               addonIcon={faServer}
        />
        {props.values.pool && (
          <React.Fragment>
            <Field name="template"
                   component={Select}
                   options={templateOptions}
                   placeholder="Select an OS template to install..."
            />
            <Field name="storage"
                   component={Select}
                   options={srOptions}
                   placeholder="Select a storage repository to install on..."
                   addonIcon={faDatabase}
            />
            <Field name="network"
                   component={Select}
                   options={networkOptions}
                   placeholder="Select a network to install on..."
            />
            <Field name="nameLabel"
                   component={Input}
                   placeholder="How you would name this VM"
                   addonIcon={faTag}
            />
            <Field name="nameDescription"
                   component={Input}
                   placeholder="Enter a description (Optional)..."
                   addonIcon={faComment}
            />
            <Field name="autoMode"
                   component={CheckBoxComponent}
                   disabled={!currentTemplateOsKind}
                   tooltip="Automode"
            >
              <h6> Unattended installation </h6>
            </Field>
            <React.Fragment>
              {props.values.autoMode && (
                <div>
                  <H4 style={{margin: '20px'}}><FormattedMessage {...messages.account} /></H4>
                  <Field name="hostname"
                         component={Input}
                         placeholder="Enter hostname..."
                         addonIcon={faDesktop}
                  />
                  <Field name="fullname"
                         component={Input}
                         placeholder="Enter your full name (Optional)..."
                         addonIcon={faSignature}
                  />
                  <Field name="username"
                         component={Input}
                         placeholder="Enter username (1-32 latin characters)..."
                         addonIcon={faUser}
                  />
                  <Field name="password"
                         component={Input}
                         placeholder="Enter password..."
                         addonIcon={faKey}
                         type="password"
                  />
                  <Field name="password2"
                         component={Input}
                         placeholder="Repeat password"
                         addonIcon={faKey}
                         type="password"
                  />
                  <h4><FormattedMessage {...messages.network} /></h4>
                  <Field name="networkType"
                         component={Select}
                         options={networkTypeOptions}
                  />
                  {props.values.networkType.value === 'static' && (
                    <React.Fragment>
                      <Field name="ip"
                             component={Input}
                             placeholder={"Enter IP address..."}
                             label={true}
                      >IP:</Field>
                      <Field name="gateway"
                             component={Input}
                             placeholder={"Enter gateway address..."}
                             label={true}
                      >Gateway:</Field>
                      <Field name="netmask"
                             component={Input}
                             placeholder={"Enter netmask address..."}
                             label={true}
                      >Netmask:</Field>
                      <Field name="dns0"
                             component={Input}
                             placeholder={"Enter DNS #1"}
                             label={true}
                      >DNS 1:</Field>
                      <Field name="dns1"
                             component={Input}
                             placeholder={"Enter DNS #2"}
                             label={true}
                      >DNS 2:</Field>
                    </React.Fragment>
                  )
                  }
                </div>
              ) || (
                <Field name="iso"
                       component={Select}
                       placeholder="Select ISO image to install from..."
                       options={isoOptions}
                />
              )
              }
              <H4><FormattedMessage {...messages.resources} /></H4>
              <Field name="vcpus"
                     component={Input}
                     type="number"
                     addonIcon={faMicrochip}
              />
              <Field name="ram"
                     component={Input}
                     type="number"
                     addonIcon={faMemory}
                     appendAddonText={"MB"}
              />
              <Field name="hdd"
                     component={Input}
                     type="number"
                     addonIcon={faHdd}
                     appendAddonText={"GB"}
              />
            </React.Fragment>
          </React.Fragment>
        )}
        <Button type="submit" primary={true}>
          Create
        </Button>

      </Form>
    </FormContext.Provider>
  )

};
export default VMForm;
