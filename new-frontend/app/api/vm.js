import axios from 'axios';
export const startStopVm = async (uuid, isStart) =>
{
  return await axios.post('api/startstopvm', { uuid, enable: isStart}
  );
};
