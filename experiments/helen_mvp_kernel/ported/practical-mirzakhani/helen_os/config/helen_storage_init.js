/**
 * HELEN OS — localStorage Persistence Layer
 * Maintains avatar consistency + chat history across sessions
 */

const HELEN_STORAGE = {
  avatar: {
    STORAGE_KEY: 'helen_avatar_v1',
    defaults: {
      hair_color: '#e84855',
      eye_color: '#4da6ff',
      cardigan_color: '#f5e6d3',
      cardigan_buttons: 8,
      pose: 'standing-centered',
      tassels: ['shoulder-left', 'shoulder-right']
    },
    save: function() {
      const state = JSON.stringify(this.defaults);
      try {
        localStorage.setItem(this.STORAGE_KEY, state);
        sessionStorage.setItem(this.STORAGE_KEY, state);
        console.log('✓ Avatar state persisted');
      } catch (e) {
        console.error('Avatar persistence failed:', e);
      }
    },
    load: function() {
      try {
        const stored = localStorage.getItem(this.STORAGE_KEY);
        return stored ? JSON.parse(stored) : this.defaults;
      } catch (e) {
        console.warn('Could not load avatar state, using defaults');
        return this.defaults;
      }
    },
    restore: function() {
      const state = this.load();
      console.log('Avatar restored:', state);
      return state;
    }
  },

  chat: {
    STORAGE_KEY: 'helen_chat_v1',
    save: function(messages) {
      try {
        const state = JSON.stringify(messages);
        localStorage.setItem(this.STORAGE_KEY, state);
        console.log(`✓ Chat history saved (${messages.length} messages)`);
      } catch (e) {
        console.error('Chat persistence failed:', e);
      }
    },
    load: function() {
      try {
        const stored = localStorage.getItem(this.STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
      } catch (e) {
        console.warn('Could not load chat history');
        return [];
      }
    }
  },

  init: function() {
    console.log('🔄 Initializing HELEN OS storage layer...');
    this.avatar.save();
    const history = this.chat.load();
    console.log(`✓ Storage initialized (avatar + ${history.length} chat messages)`);
  }
};

// Auto-init on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => HELEN_STORAGE.init());
} else {
  HELEN_STORAGE.init();
}
