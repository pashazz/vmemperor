/*
 * Templates Messages
 *
 * This contains all the text for the Templates component.
 */
import { defineMessages } from 'react-intl';

export default defineMessages({
  todo: {
    id: 'app.components.Templates.todo',
    defaultMessage: 'TODO',
  },
  generators: {
    id: 'app.components.Templates.generators',
    defaultMessage: 'The following list of templates is able to work with VM emperor system but no one has implemented automatic installer instructions generator. For this moment only <a href="http://en.wikipedia.org/wiki/Preseed">preseed-generator</a> is available, commits are welcome.',
  },
  notUsable: {
    id: 'app.components.Templates.notUsable',
    defaultMessage: 'The templates you can not use <i>yet</i>',
  },
});
