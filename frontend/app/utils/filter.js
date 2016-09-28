function checkFilter(item, column, value = '') {
  let toCheck = '';
  if (typeof item[column] === 'function') {
    toCheck = item[column]();
  } else {
    toCheck = item[column] || '';
  }

  const trimmed = value.trim();
  return trimmed === '' || toCheck.toLowerCase().indexOf(trimmed.toLowerCase()) > -1;
}

export function filterItems(items, filters) {
  return items.filter(item => Object.keys(filters).reduce((ac, column) => ac && checkFilter(item, column, filters[column]), true));
}
