import 'whatwg-fetch';

const status = function(response) {
  if (response.status >= 200 && response.status < 300) {
    return response;
  } else {
      var error = new Error(response.statusText);
      error.response = response;
      throw response;
  }
}

const json = function(response) {
  return response.json()
}

export function GET(url) {
  return fetch(url, {
      credentials: 'same-origin'
    })
    .then(status)
    .then(json);
}

export function POST(url, form) {
  return fetch(url, {
      credentials: 'same-origin',
      method: 'post',
      body: JSON.stringify(form)
    })
    .then(status)
    .then(json);
}
