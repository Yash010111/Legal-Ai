import React, { useEffect, useState, useRef } from 'react';
import { SafeAreaView, View, Text, TextInput, FlatList, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEY_URL = '@mcp_server_url';

export default function App() {
  const [serverUrl, setServerUrl] = useState('https://aafb074a34b4.ngrok-free.app/query');
  const [urlEdit, setUrlEdit] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const flatRef = useRef();

  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem(STORAGE_KEY_URL);
        if (saved) {
          setServerUrl(saved);
          setUrlEdit(saved);
        } else {
          setUrlEdit(serverUrl);
        }
      } catch (e) {
        console.warn('Failed to load saved server URL', e);
        setUrlEdit(serverUrl);
      }
    })();
  }, []);

  const saveUrl = async () => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY_URL, urlEdit);
      setServerUrl(urlEdit);
    } catch (e) {
      console.warn('Failed to save server URL', e);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const text = input.trim();
    const userMsg = { id: Date.now().toString(), sender: 'user', text };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setLoading(true);

    // Determine target URL. If user provided a base URL (no path), default to /query endpoint
    let target = serverUrl;
    try {
      const parsed = new URL(serverUrl);
      // If path is empty or just '/', prefer the /query endpoint
      if (!parsed.pathname || parsed.pathname === '/') {
        parsed.pathname = '/query';
        target = parsed.toString();
      }
    } catch (e) {
      // If invalid URL (user may have omitted scheme), try to treat as host with http
      try {
        const parsed2 = new URL(`http://${serverUrl}`);
        if (!parsed2.pathname || parsed2.pathname === '/') {
          parsed2.pathname = '/query';
          target = parsed2.toString();
        } else {
          target = parsed2.toString();
        }
      } catch (err) {
        // fallback to raw serverUrl
        target = serverUrl;
      }
    }

    // Send to target; prefer /query request shape { question: string }
    try {
      const res = await fetch(target, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      });

      let assistantText = '';
      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const data = await res.json();
        // server's /query returns { answer, confidence, sources }
        if (data.answer) assistantText = data.answer;
        else if (data.reply) assistantText = data.reply;
        else if (data.response) assistantText = data.response;
        else assistantText = JSON.stringify(data);
      } else {
        assistantText = await res.text();
      }

      const botMsg = { id: (Date.now()+1).toString(), sender: 'assistant', text: assistantText };
      setMessages((m) => [...m, botMsg]);
    } catch (e) {
      const errMsg = { id: (Date.now()+2).toString(), sender: 'assistant', text: `Error: ${e.message}` };
      setMessages((m) => [...m, errMsg]);
    } finally {
      setLoading(false);
      setTimeout(() => flatRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  const renderItem = ({ item }) => (
    <View style={[styles.bubble, item.sender === 'user' ? styles.userBubble : styles.botBubble]}>
      <Text style={[styles.bubbleText, item.sender === 'assistant' && styles.botText]}>{item.text}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>MCP Chat Client</Text>
      </View>

      <View style={styles.urlRow}>
        <TextInput style={styles.urlInput} value={urlEdit} onChangeText={setUrlEdit} placeholder="Enter server URL (e.g. http://localhost:3000)" />
        <TouchableOpacity style={styles.saveBtn} onPress={saveUrl}>
          <Text style={styles.saveBtnText}>Save</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={flatRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.messages}
      />

      {loading && (
        <View style={styles.loadingRow}>
          <ActivityIndicator />
          <Text style={{ marginLeft: 8 }}>Waiting for server...</Text>
        </View>
      )}

      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <View style={styles.inputRow}>
          <TextInput value={input} onChangeText={setInput} placeholder="Type a message" style={styles.input} onSubmitEditing={sendMessage} returnKeyType="send" />
          <TouchableOpacity style={styles.sendBtn} onPress={sendMessage}>
            <Text style={styles.sendBtnText}>Send</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f6f6f6' },
  header: { padding: 12, backgroundColor: '#2b6ef6', alignItems: 'center' },
  title: { color: 'white', fontSize: 18, fontWeight: '600' },
  urlRow: { flexDirection: 'row', padding: 8, alignItems: 'center' },
  urlInput: { flex: 1, borderColor: '#ddd', borderWidth: 1, borderRadius: 6, padding: 8, backgroundColor: 'white' },
  saveBtn: { marginLeft: 8, backgroundColor: '#2b6ef6', paddingHorizontal: 12, paddingVertical: 10, borderRadius: 6 },
  saveBtnText: { color: 'white', fontWeight: '600' },
  messages: { paddingHorizontal: 12, paddingVertical: 8 },
  bubble: { marginVertical: 6, padding: 10, borderRadius: 8, maxWidth: '85%' },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#2b6ef6' },
  botBubble: { alignSelf: 'flex-start', backgroundColor: '#e5e7eb' },
  bubbleText: { color: 'white' },
  botText: { color: '#111' },
  inputRow: { flexDirection: 'row', padding: 8, borderTopColor: '#eee', borderTopWidth: 1, backgroundColor: 'white' },
  input: { flex: 1, padding: 10, borderRadius: 6, borderColor: '#ddd', borderWidth: 1, backgroundColor: '#fff' },
  sendBtn: { marginLeft: 8, backgroundColor: '#10b981', paddingHorizontal: 12, paddingVertical: 10, borderRadius: 6 },
  sendBtnText: { color: 'white', fontWeight: '600' },
  loadingRow: { flexDirection: 'row', alignItems: 'center', padding: 8 }
});
