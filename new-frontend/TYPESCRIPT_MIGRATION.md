# The results of a migration process are available in `typescript` branch

1. `npm install -D ts-node typescript ts-loader fork-ts-checker-webpack-plugin`
`ts-node` is a nice typescript interpreter to play around. Run with `npx ts-node`

2. `npm install -D @types/react  @types/react-redux @types/react-router-redux @types/react-router @types/react-dom @types/webpack-env @types/react-intl `

3. Edit webpack config files so that they use `ts-loader` to load tsx files (see `typescript` branch)

4. rename `app/app.js` to `app/app.tsx` and fix relative imports

5. create `tsconfig.json` as seen in `typescript` branch

6. at this point we encountered the following error while doing `npm run build:dll`:

```
ERROR in /home/pasha/vmemperor/new-frontend/app/app.tsx
ERROR in /home/pasha/vmemperor/new-frontend/app/app.tsx(97,13):
TS2339: Property 'Intl' does not exist on type 'Window'.
```

We surpass it by declaring Intl:
```js
declare global{
  interface Window {
    Intl: any,
  }
}
```

7. Then it'd run but imports wouldn't work as the default TypeScript import syntax is
```js
import * as React from 'react';
```

So we added new `esModuleInterop` compiler argument for ES6 modules import (see tsconfig.json)
