import axios from 'axios'
const playbooks = async () =>
{
  return await axios.get('/api/playbooks');
};

export const execplaybook = async(playbook, vms, args) =>
{
  return await axios.post('/api/executeplaybook', {playbook, vms, ...args})
};

export const pbstatus = async(taskid) =>
{
  console.log("Requesting playbook status: ", taskid);
  return await axios.post('/api/playbookstatus', {taskid});
};

export default playbooks;
