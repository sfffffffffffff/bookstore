import { createStore } from 'vuex'
import createPersistedState from 'vuex-persistedstate'
// store.js


export default createStore({
  state: {
    token: localStorage.getItem('token') || null,
    userInfo: null
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    setUser(state, userInfo) {
      state.userInfo = userInfo
    },
    clearUser(state) {
      state.token = null
      state.userInfo = null
      localStorage.removeItem('token')
    }
  }
})