const status = function(response) {
  if (response.status >= 200 && response.status < 300) {
      return response
  }
  throw new Error(response.statusText)
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
      method: 'post',
      credentials: 'same-origin',
      body: JSON.stringify(form)
    })
    .then(status)
    .then(json);
}
