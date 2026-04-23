import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Import Unnnic Design System
import Unnnic from '@weni/unnnic-system';
import '@weni/unnnic-system/dist/style.css';

const app = createApp(App);

app.use(router);
app.use(Unnnic);

app.mount('#app');
