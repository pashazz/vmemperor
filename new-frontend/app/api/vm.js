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
