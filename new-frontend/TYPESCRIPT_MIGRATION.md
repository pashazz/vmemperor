1. `npm install -D ts-node typescript awesome-typescript-loader`
`ts-node` is a nice typescript interpreter to play around. Run with `npx ts-node`

2. `npm install -D @types/react  @types/react-redux @types/react-router-redux @types/react-router @types/react-dom`
3. in `webpack/webpack.base.babel.js` edit:
    - add
    ```
    const TsConfigPathsPlugin = require('awesome-typescript-loader').TsConfigPathsPlugin;
    const CheckerPlugin = require('awesome-typescript-loader').CheckerPlugin;
    ```
    - into `module: plugins: options.plugins.concat([...` add:
    ```js
     new TsConfigPathsPlugin(),
     new CheckerPlugin(),
    ```
    - into `resolve: extensions` add `'.ts'`
    - into `module: rules` add
    ```js
    {
      test: /\.ts?$/,
      use: options.tsLoaders,
    },
    ```

4. in `webpack/webpack.dev.babel.js` edit:
   - edit `entry`, replace `app/app.js` with `app/app.ts`
   - add new to exports:
   ```js
     tsLoaders: [
    'react-hot-loader',
    'awesome-typescript-loader',
  ],
  ```

5.  in `webpack/webpack.prod.babel.js` edit:
   - edit `entry`, replace `app/app.js` with `app/app.ts`
   - add new to exports:
   ```js
     tsLoaders:'awesome-typescript-loader',
  ```
6. rename `app/app.js` to `app/app.ts`

7. create `tsconfig.json` with the following contents:
