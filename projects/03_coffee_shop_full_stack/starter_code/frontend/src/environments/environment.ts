/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'coffee-api-server.us.auth0.com', // the auth0 domain prefix
    audience: 'drinks', // the audience set for the auth0 app
    clientId: 'xnHinEU21DQ3dd1imvTdAaimiy8Q56C3', // the client id generated for the auth0 app
    callbackURL: 'https://localhost:8080/login-result', // the base url of the running ionic application. 
  }
};
