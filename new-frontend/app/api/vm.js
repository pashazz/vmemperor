import axios from 'axios';
export const startStopVm = async (uuid, isStart) =>
{
  return await axios.post('/api/startstopvm', { uuid, enable: isStart});
};

export const destroyVm = async (uuid) =>
{
  return await axios.post('/api/destroyvm', { uuid });
};

export const vnc = async(uuid) =>
{
  return await axios.post('/api/vnc', { uuid });
};

export const reboot = async(uuid) =>
{
  return await axios.post('/api/rebootvm', { uuid});
};

export const convert = async(uuid, mode) =>
{
  return await axios.post('/api/convertvm', {uuid, mode});
};

export const diskInfo = async (uuid) =>
{
  return await axios.post('/api/vmdiskinfo', {uuid});
};
