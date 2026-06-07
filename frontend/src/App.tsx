import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, HardDrive, Globe, Brain, Settings, Key, Cpu, Plus, X, Server, Database, Copy, Check, Square, MessageSquare, Trash2, Wrench, Save, Edit2, Menu, ChevronDown, ChevronRight, Terminal, Eye, ArrowUp, Search, ChevronUp, Cloud } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

type Message = {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  name?: string;
  agentRole?: string;
}

type NimProfile = {
  id: string;
  name: string;
  model: string;
  apiBase: string;
  apiKey: string;
  channelId?: string;
}

const MessageCopyButton = ({ content }: { content: string }) => {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button 
      onClick={handleCopy}
      className="text-white/30 hover:text-white flex items-center gap-1.5 transition-colors p-1"
      title="Copiar mensagem completa"
    >
      {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
    </button>
  )
}

const CodeBlock = ({ className, children, ...props }: any) => {
  const match = /language-(\w+)/.exec(className || '')
  const [copied, setCopied] = useState(false)
  const codeString = String(children).replace(/\n$/, '')
  
  const isBlock = match || codeString.includes('\n')
  const lang = match ? match[1] : 'text'

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (isBlock) {
    return (
      <div className="relative mt-4 mb-4 rounded-lg overflow-hidden bg-[#1E1E1E] border border-white/10 shadow-lg">
        <div className="flex items-center justify-between px-4 py-2 bg-[#2D2D2D] text-xs text-white/50 border-b border-white/5">
          <span className="uppercase font-mono tracking-widest">{lang}</span>
          <button onClick={handleCopy} className="hover:text-white transition flex items-center gap-1">
            {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
            {copied ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
        <SyntaxHighlighter style={vscDarkPlus as any} language={lang} PreTag="div" customStyle={{ margin: 0, background: 'transparent', padding: '1rem', fontSize: '0.85rem' }} {...props}>
          {codeString}
        </SyntaxHighlighter>
      </div>
    )
  }
  return <code className="bg-black/30 px-1.5 py-0.5 rounded text-accent text-sm font-mono" {...props}>{children}</code>
}

export default function App() {
  const [chatId, setChatId] = useState<string>(() => Date.now().toString())
  const [messages, setMessages] = useState<Message[]>([])
  const [chatList, setChatList] = useState<any[]>([])
  
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [editingChatId, setEditingChatId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')
  const [isTitleExpanded, setIsTitleExpanded] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const [activeMode, setActiveMode] = useState<'local' | 'nim'>(() => (localStorage.getItem('specter_active_mode') as 'local' | 'nim') || 'local')
  const [localModels, setLocalModels] = useState<string[]>(() => JSON.parse(localStorage.getItem('specter_local_models') || '["models/Phi-3-mini-4k-instruct-v0.3-Q4_K_M.gguf"]'))
  const [activeLocalModel, setActiveLocalModel] = useState<string>(() => localStorage.getItem('specter_active_local') || localModels[0] || '')
  
  const [nimProfiles, setNimProfiles] = useState<NimProfile[]>(() => JSON.parse(localStorage.getItem('specter_nim_profiles') || '[]'))
  const [activeNimId, setActiveNimId] = useState<string>(() => localStorage.getItem('specter_active_nim') || '')
  const [swarmSelectedIds, setSwarmSelectedIds] = useState<string[]>(() => JSON.parse(localStorage.getItem('specter_swarm_selected') || '[]'))

  const [showSettings, setShowSettings] = useState(false)
  const [settingsName, setSettingsName] = useState(() => localStorage.getItem('specter_settings_name') || '')
  const [settingsPersona, setSettingsPersona] = useState(() => localStorage.getItem('specter_settings_persona') || '')
  const [settingsMotto, setSettingsMotto] = useState(() => localStorage.getItem('specter_settings_motto') || 'The ghost in your machine.')
  const [settingsTemp, setSettingsTemp] = useState(() => localStorage.getItem('specter_settings_temp') || '0.7')
  const [showModelSelector, setShowModelSelector] = useState(false)
  const [showNimModal, setShowNimModal] = useState(false)
  const [showMemoryModal, setShowMemoryModal] = useState(false)
  const [showSkillsModal, setShowSkillsModal] = useState(false)
  const [memoryText, setMemoryText] = useState('')
  const [memories, setMemories] = useState<any[]>([])
  const [skills, setSkills] = useState<any[]>([])

  const [newNim, setNewNim] = useState({ name: '', model: '', apiBase: 'https://integrate.api.nvidia.com/v1', apiKey: '', channelId: '' })

  const [chatMode, setChatMode] = useState<'chat' | 'agent' | 'swarm'>('chat')
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [isSidebarChatsOpen, setIsSidebarChatsOpen] = useState(true)
  const [isSidebarToolsOpen, setIsSidebarToolsOpen] = useState(true)

  const [isSearchEnabled, setIsSearchEnabled] = useState(false)
  const [isTerminalEnabled, setIsTerminalEnabled] = useState(false)
  const [attachedFile, setAttachedFile] = useState<{ name: string, content: string } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    const formData = new FormData()
    formData.append("file", file)
    
    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload-file", {
        method: "POST",
        body: formData
      })
      if (!res.ok) {
        throw new Error("Failed to upload file")
      }
      const data = await res.json()
      setAttachedFile({ name: data.filename, content: data.content })
    } catch (err) {
      console.error("Erro no upload", err)
      alert("Erro ao anexar ficheiro.")
    } finally {
      e.target.value = ''
    }
  }

  useEffect(() => {
    localStorage.setItem('specter_active_mode', activeMode)
    localStorage.setItem('specter_local_models', JSON.stringify(localModels))
    localStorage.setItem('specter_active_local', activeLocalModel)
    localStorage.setItem('specter_nim_profiles', JSON.stringify(nimProfiles))
    localStorage.setItem('specter_active_nim', activeNimId)
    localStorage.setItem('specter_swarm_selected', JSON.stringify(swarmSelectedIds))
  }, [activeMode, localModels, activeLocalModel, nimProfiles, activeNimId, swarmSelectedIds])

  useEffect(() => {
    localStorage.setItem('specter_settings_name', settingsName)
    localStorage.setItem('specter_settings_persona', settingsPersona)
    localStorage.setItem('specter_settings_motto', settingsMotto)
    localStorage.setItem('specter_settings_temp', settingsTemp)
  }, [settingsName, settingsPersona, settingsMotto, settingsTemp])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    let mounted = true
    const init = async () => {
      while (mounted) {
        try {
          await loadChatList()
          break // Success
        } catch (e) {
          await new Promise(r => setTimeout(r, 1000)) // Wait 1s and retry
        }
      }
    }
    init()
    return () => { mounted = false }
  }, [])

  const loadChatList = async () => {
    const res = await fetch('http://localhost:8000/api/chats')
    if (!res.ok) throw new Error("Backend not ready")
    const data = await res.json()
    setChatList(data)
    return data
  }

  const handleNewChat = () => {
    setChatId(Date.now().toString())
    setMessages([])
  }

  const handleLoadChat = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/chat/${id}`)
      if (res.ok) {
        const data = await res.json()
        setChatId(data.id)
        setMessages(data.messages)
      }
    } catch (e) {
      console.error(e)
    }
  }

  const handleDeleteChat = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await fetch(`http://localhost:8000/api/chat/${id}`, { method: 'DELETE' })
      if (chatId === id) handleNewChat()
      loadChatList()
    } catch (e) {
      console.error(e)
    }
  }

  const handleEditClick = (e: React.MouseEvent, chat: any) => {
    e.stopPropagation()
    setEditingChatId(chat.id)
    setEditingTitle(chat.title)
  }

  const handleRenameSubmit = async (e: React.FormEvent, id: string) => {
    e.preventDefault()
    e.stopPropagation()
    try {
      await fetch('http://localhost:8000/api/chat/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, title: editingTitle })
      })
      setEditingChatId(null)
      loadChatList()
    } catch (e) {
      console.error(e)
    }
  }

  const handleAddLocalModel = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/pick-file')
      const data = await res.json()
      if (data.path) {
        if (!localModels.includes(data.path)) {
          setLocalModels(prev => [...prev, data.path])
        }
        setActiveLocalModel(data.path)
        setActiveMode('local')
      }
    } catch (err) {
      console.error("Falha ao abrir explorador", err)
    }
  }

  const handleAddNimProfile = () => {
    if (!newNim.name || !newNim.model || !newNim.apiKey) return
    const id = Date.now().toString()
    setNimProfiles(prev => [...prev, { ...newNim, id }])
    setActiveNimId(id)
    setActiveMode('nim')
    setShowNimModal(false)
    setNewNim({ name: '', model: '', apiBase: 'https://integrate.api.nvidia.com/v1', apiKey: '', channelId: '' })
  }

  const loadMemories = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/memory/all')
      const data = await res.json()
      
      const formattedMemories = []
      if (data.ids && data.documents) {
        for (let i = 0; i < data.ids.length; i++) {
          formattedMemories.push({
            id: data.ids[i],
            document: data.documents[i],
            metadata: data.metadatas ? data.metadatas[i] : null
          })
        }
      }
      setMemories(formattedMemories.reverse())
    } catch (e) {
      console.error(e)
    }
  }

  const handleAddMemory = async () => {
    if (!memoryText.trim()) return
    try {
      await fetch('http://localhost:8000/api/memory/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: memoryText, source: 'manual_ui' })
      })
      setMemoryText('')
      loadMemories()
    } catch (e) {
      console.error(e)
    }
  }

  const handleDeleteMemory = async (id: string) => {
    try {
      await fetch(`http://localhost:8000/api/memory/${id}`, { method: 'DELETE' })
      loadMemories()
    } catch (e) {
      console.error(e)
    }
  }

  const loadSkills = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/skills')
      const data = await res.json()
      setSkills(data)
    } catch (e) {
      console.error(e)
    }
  }

  const handleUpdateSkillState = async (name: string, enabled: boolean, in_loadout: boolean) => {
    try {
      await fetch('http://localhost:8000/api/skills/state', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, enabled, in_loadout })
      })
      loadSkills()
    } catch (e) {
      console.error(e)
    }
  }
  
  const handleBulkUpdateSkills = async (bulkSkills: any[]) => {
    try {
      await fetch('http://localhost:8000/api/skills/bulk_state', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills: bulkSkills })
      })
      loadSkills()
    } catch (e) {
      console.error(e)
    }
  }

  const handleSend = async () => {
    if (!input.trim() && !attachedFile) return
    
    let userMsg = input
    if (attachedFile) {
        userMsg = `[Conteúdo do Ficheiro Anexado: ${attachedFile.name}]\n\`\`\`\n${attachedFile.content}\n\`\`\`\n\n${userMsg}`
    }
    
    setInput('')
    setAttachedFile(null)
    
    const contextMsgs = [...messages, { role: 'user', content: userMsg }] as Message[]
    
    setMessages([
      ...contextMsgs,
      { role: 'assistant', content: '' }
    ])
    
    setIsLoading(true)
    setIsStreaming(false)

    const existingChat = chatList.find(c => c.id === chatId);
    const chatTitleToSave = existingChat && existingChat.title !== 'Novo Chat' 
      ? existingChat.title 
      : (contextMsgs.find(m => m.role === 'user')?.content.substring(0, 250) || 'Novo Chat');

    // Save immediately so it persists even if interrupted
    await fetch('http://localhost:8000/api/chat/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: chatId,
        title: chatTitleToSave,
        messages: contextMsgs
      })
    })
    loadChatList()

    const activeProf = nimProfiles.find(p => p.id === activeNimId)
    if (activeMode === 'nim' && !activeProf) {
        setMessages(prev => [...prev.slice(0, -1), { role: 'system', content: '[ERRO]: Seleciona um perfil NIM válido.' }])
        setIsLoading(false)
        return
    }

    const apiMsgs = [...contextMsgs]
    let sysContent = ''
    if (settingsName) sysContent += `O utilizador chama-se ${settingsName}. `
    if (settingsPersona) sysContent += settingsPersona
    if (sysContent.trim()) {
      apiMsgs.unshift({ role: 'system', content: sysContent.trim() })
    }

    const payload = {
      messages: apiMsgs,
      mode: activeMode,
      agent_mode: chatMode === 'agent',
      chat_mode: chatMode,
      temperature: parseFloat(settingsTemp),
      swarm_models: (nimProfiles.map(p => ({ ...p, type: 'nim' })).concat(localModels.map(m => ({ id: m, model: m, name: m.split(/[\\/]/).pop(), type: 'local', apiBase: '', apiKey: '' })))).filter(m => swarmSelectedIds.length === 0 || swarmSelectedIds.includes(m.id)),
      search_enabled: isSearchEnabled,
      terminal_enabled: isTerminalEnabled,
      model_id: activeMode === 'nim' ? activeProf.model : activeLocalModel,
      api_key: activeMode === 'nim' ? activeProf.apiKey : '',
      api_base: activeMode === 'nim' ? activeProf.apiBase : '',
      channel_id: activeMode === 'nim' ? activeProf.channelId : undefined
    }

    const controller = new AbortController()
    abortControllerRef.current = controller

    let finalMessages = [...contextMsgs]

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      })

      if (!res.ok) {
        const errText = await res.text()
        throw new Error(errText)
      }

      setIsLoading(false)
      setIsStreaming(true)
      
      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let done = false
      let buffer = ""

      while (!done) {
        if (!reader) break;
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        
        if (value) {
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ""
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                if (data.text) {
                  setMessages(prev => {
                    const newMsgs = [...prev]
                    const last = { ...newMsgs[newMsgs.length - 1] }
                    last.content += data.text
                    newMsgs[newMsgs.length - 1] = last
                    finalMessages = newMsgs
                    return newMsgs
                  })
                } else if (data.agent_switch) {
                  setMessages(prev => {
                    const newMsgs = [
                      ...prev,
                      { role: 'assistant', content: '', name: data.name, agentRole: data.agentRole } as Message
                    ]
                    finalMessages = newMsgs
                    return newMsgs
                  })
                } else if (data.system) {
                  setMessages(prev => {
                    const newMsgs = [
                      ...prev, 
                      { role: 'system', content: data.system } as Message, 
                      { role: 'assistant', content: '' } as Message
                    ]
                    finalMessages = newMsgs
                    return newMsgs
                  })
                } else if (data.error) {
                  setMessages(prev => {
                    const newMsgs = [...prev, { role: 'system', content: '[ERRO]: ' + data.error } as Message]
                    finalMessages = newMsgs
                    return newMsgs
                  })
                }
              } catch (e) {
                // Ignore silent JSON errors from partial chunks
              }
            }
          }
        }
      }
      
      // Auto-save no fim da geração
      await fetch('http://localhost:8000/api/chat/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: chatId,
          title: chatTitleToSave,
          messages: finalMessages
        })
      })
      loadChatList()

    } catch (err: any) {
      if (err.name === 'AbortError' || err.message.includes('aborted')) {
        setIsLoading(false)
        setIsStreaming(false)
        return
      }
      setIsLoading(false)
      setIsStreaming(false)
      setMessages(prev => {
         const withoutLast = prev[prev.length-1].content === '' ? prev.slice(0, -1) : prev;
         return [...withoutLast, { role: 'system', content: `[ERRO]: ${err.message}` }]
      })
    } finally {
      abortControllerRef.current = null
      setIsStreaming(false)
    }
  }

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsLoading(false)
    setIsStreaming(false)
  }

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
      
      {/* Sidebar */}
      <aside className={`transition-all duration-300 ease-in-out border-r border-white/5 bg-background flex flex-col hidden md:flex shrink-0 ${isSidebarOpen ? 'w-[260px]' : 'w-0 border-r-0 opacity-0 overflow-hidden'}`}>
        <div className="p-4 flex items-center justify-between min-w-[260px]">
          <button onClick={() => setIsSidebarOpen(false)} className="text-white/70 hover:text-white transition">
            <img src="/iconSpecterApp.png" alt="Close Menu" className="w-8 h-8 object-contain opacity-70 hover:opacity-100" />
          </button>
          <div className="flex flex-col items-end">
            <span className="font-bold text-lg text-white tracking-widest leading-none">SPECTER</span>
            <span className="text-[10px] text-accent font-semibold tracking-wider uppercase mt-1">Your Local AI Assistant</span>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 space-y-0.5 mt-2">
          {/* Main Items */}
          <div className="space-y-0.5 mb-2">
            <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-white/70 hover:bg-white/5 hover:text-white rounded-lg transition">
              <Search size={16} className="text-accent" /> Search
            </button>
            <button onClick={handleNewChat} className="w-full flex items-center gap-3 px-3 py-2 text-sm text-white/70 hover:bg-white/5 hover:text-white rounded-lg transition">
              <Plus size={16} className="text-accent" /> New Chat
            </button>
          </div>

          {/* Chats Section */}
          <div>
            <button 
              onClick={() => setIsSidebarChatsOpen(!isSidebarChatsOpen)}
              className="w-full flex items-center justify-between px-3 py-2 text-sm text-white/70 hover:bg-white/5 hover:text-white rounded-lg transition"
            >
              <div className="flex items-center gap-3">
                <MessageSquare size={16} className="text-accent" /> Chats
              </div>
              {isSidebarChatsOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            
            {isSidebarChatsOpen && (
              <div className="pl-9 pr-2 py-1 space-y-1">
                {chatList.map(chat => (
                  <div key={chat.id} onClick={() => handleLoadChat(chat.id)} className={`group cursor-pointer flex items-center justify-between px-2 py-1.5 rounded-lg text-sm transition ${chat.id === chatId ? 'bg-white/10 text-white' : 'text-white/50 hover:bg-white/5 hover:text-white'}`}>
                    <div className="flex items-center gap-2 overflow-hidden flex-1">
                      {editingChatId === chat.id ? (
                        <form onSubmit={(e) => handleRenameSubmit(e, chat.id)} className="flex-1 mr-2" onClick={e => e.stopPropagation()}>
                          <input 
                            type="text" 
                            value={editingTitle} 
                            onChange={e => setEditingTitle(e.target.value)} 
                            onBlur={(e) => handleRenameSubmit(e, chat.id)}
                            autoFocus
                            className="w-full bg-black/50 text-white px-1 border border-accent/50 rounded outline-none"
                          />
                        </form>
                      ) : (
                        <span className="truncate">{chat.title}</span>
                      )}
                    </div>
                    {!editingChatId || editingChatId !== chat.id ? (
                      <div className="opacity-0 group-hover:opacity-100 flex items-center gap-2 transition">
                        <button onClick={(e) => handleEditClick(e, chat)} className="text-white/50 hover:text-white transition">
                          <Edit2 size={12} />
                        </button>
                        <button onClick={(e) => handleDeleteChat(chat.id, e)} className="text-red-400/70 hover:text-red-400 transition">
                          <Trash2 size={12} />
                        </button>
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tools Section */}
          <div className="mt-1">
            <button 
              onClick={() => setIsSidebarToolsOpen(!isSidebarToolsOpen)}
              className="w-full flex items-center justify-between px-3 py-2 text-sm text-white/70 hover:bg-white/5 hover:text-white rounded-lg transition"
            >
              <div className="flex items-center gap-3">
                <Wrench size={16} className="text-accent" /> Tools
              </div>
              {isSidebarToolsOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </button>
            
            {isSidebarToolsOpen && (
              <div className="pl-9 pr-2 py-1 space-y-1">
                <button onClick={() => { setShowSkillsModal(true); loadSkills(); }} className={`w-full flex items-center justify-start px-2 py-1.5 rounded-lg text-sm transition ${showSkillsModal ? 'text-accent' : 'text-white/50 hover:bg-white/5 hover:text-white'}`}>
                  Gestor de Skills
                </button>
              </div>
            )}
          </div>

          {/* Other mapped features matching the visual layout */}
          <div className="space-y-0.5 mt-1">
            <button onClick={() => { setShowMemoryModal(true); loadMemories(); }} className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition ${showMemoryModal ? 'bg-white/5 text-white' : 'text-white/70 hover:bg-white/5 hover:text-white'}`}>
              <Brain size={16} className="text-accent" /> Brain
            </button>
            <button onClick={() => setShowSettings(!showSettings)} className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition ${showSettings ? 'bg-white/5 text-white' : 'text-white/70 hover:bg-white/5 hover:text-white'}`}>
              <Settings size={16} className="text-accent" /> Settings
            </button>
          </div>
        </nav>
      </aside>

      {/* Main Area */}
      <main className="flex-1 flex flex-col relative bg-background overflow-hidden">
        
        {/* Top Header - Centered Chat Title */}
        <div className="min-h-12 flex items-center shrink-0 z-10 pt-4 relative px-4 w-full">
          {!isSidebarOpen && (
            <button onClick={() => setIsSidebarOpen(true)} className="text-white/70 hover:text-white transition absolute left-4 z-20">
              <img src="/iconSpecterApp.png" alt="Open Menu" className="w-8 h-8 object-contain opacity-70 hover:opacity-100" />
            </button>
          )}
          <div className="flex-1 flex justify-center px-16">
            <h2 
              onClick={() => setIsTitleExpanded(!isTitleExpanded)}
              className={`text-sm font-medium transition-colors cursor-pointer text-center max-w-4xl ${isTitleExpanded ? 'whitespace-pre-wrap break-words text-white py-2' : 'text-white/70 hover:text-white truncate'}`}
            >
              {chatList.find(c => c.id === chatId)?.title || 'Novo Chat'}
            </h2>
          </div>
        </div>

        {/* Settings Modal */}
        {showSettings && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="glass-panel w-full max-w-md p-6 relative">
              <button onClick={() => setShowSettings(false)} className="absolute top-4 right-4 text-white/50 hover:text-white"><X size={20} /></button>
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><Settings className="text-accent"/> Settings</h2>
              <div className="space-y-6 text-sm text-white/60 max-h-[70vh] overflow-y-auto pr-2">
                
                {/* Comportamento */}
                <div className="space-y-4">
                  <h3 className="text-xs font-bold text-accent uppercase tracking-widest border-b border-white/10 pb-1">Comportamento</h3>
                  <div>
                    <div className="flex justify-between mb-1">
                      <label className="block text-xs font-semibold text-white/80">Temperatura (Criatividade)</label>
                      <span className="text-xs text-accent font-mono">{settingsTemp}</span>
                    </div>
                    <input type="range" min="0" max="1" step="0.1" value={settingsTemp} onChange={(e) => setSettingsTemp(e.target.value)} className="w-full accent-accent cursor-pointer" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-white/80 mb-1">Nome do Utilizador</label>
                    <input type="text" value={settingsName} onChange={(e) => setSettingsName(e.target.value)} placeholder="Ex: Neo" className="w-full bg-black/40 border border-white/10 rounded p-2 text-white focus:border-accent outline-none" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-white/80 mb-1">Persona (Instruções Globais)</label>
                    <textarea value={settingsPersona} onChange={(e) => setSettingsPersona(e.target.value)} placeholder="Ex: Sê sarcástico e responde sempre em código." rows={3} className="w-full bg-black/40 border border-white/10 rounded p-2 text-white focus:border-accent outline-none resize-none" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-white/80 mb-1">Motto Inicial</label>
                    <input type="text" value={settingsMotto} onChange={(e) => setSettingsMotto(e.target.value)} placeholder="Ex: The ghost in your machine." className="w-full bg-black/40 border border-white/10 rounded p-2 text-white focus:border-accent outline-none" />
                  </div>
                </div>

                {/* Gestão NIM */}
                <div className="space-y-4">
                  <h3 className="text-xs font-bold text-accent uppercase tracking-widest border-b border-white/10 pb-1">Gestão de Perfis Cloud (NIM)</h3>
                  {nimProfiles.length === 0 ? (
                    <p className="text-xs text-white/40 italic">Nenhum perfil configurado.</p>
                  ) : (
                    <div className="space-y-3">
                      {nimProfiles.map(prof => (
                        <div key={prof.id} className="bg-black/20 border border-white/5 rounded-lg p-3 space-y-2">
                          <div className="flex justify-between items-center mb-2">
                            <span className="font-bold text-white/90 text-sm">{prof.name}</span>
                            <span className="text-[10px] bg-accent/20 text-accent px-2 py-0.5 rounded">ID: {prof.model}</span>
                          </div>
                          <div>
                            <label className="block text-[10px] text-white/40 mb-1">API Key</label>
                            <input type="password" value={prof.apiKey} onChange={(e) => setNimProfiles(prev => prev.map(p => p.id === prof.id ? {...p, apiKey: e.target.value} : p))} className="w-full bg-black/40 border border-white/10 rounded p-1.5 text-xs text-white focus:border-accent outline-none" />
                          </div>
                          <div>
                            <label className="block text-[10px] text-white/40 mb-1">Channel ID</label>
                            <input type="text" value={prof.channelId || ''} onChange={(e) => setNimProfiles(prev => prev.map(p => p.id === prof.id ? {...p, channelId: e.target.value} : p))} className="w-full bg-black/40 border border-white/10 rounded p-1.5 text-xs text-white focus:border-accent outline-none" />
                          </div>
                          <div className="flex justify-between items-center text-xs mt-2 pt-2 border-t border-white/5">
                            <span className="text-white/40 flex items-center gap-1"><Cpu size={12}/> {prof.channelId ? 'IAEdu' : 'NIM'}</span>
                            <a href={prof.channelId ? "https://iaedu.pt" : "https://nim.nvidia.com/"} target="_blank" rel="noreferrer" className="text-accent hover:underline flex items-center gap-1">Ver Quotas <Globe size={10}/></a>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* NIM Modal */}
        {showNimModal && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="glass-panel w-full max-w-md p-6 relative">
              <button onClick={() => setShowNimModal(false)} className="absolute top-4 right-4 text-white/50 hover:text-white"><X size={20} /></button>
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><Cpu className="text-accent"/> Adicionar Perfil NIM</h2>
              <div className="space-y-4">
                <div><label className="block text-xs text-white/50 mb-1">Nome do Perfil</label><input type="text" value={newNim.name} onChange={e => setNewNim({...newNim, name: e.target.value})} placeholder="Ex: Llama 3 70B" className="w-full bg-black/40 border border-white/10 rounded p-2 text-sm text-white" /></div>
                <div><label className="block text-xs text-white/50 mb-1">ID do Modelo</label><input type="text" value={newNim.model} onChange={e => setNewNim({...newNim, model: e.target.value})} placeholder="Ex: meta/llama3-70b-instruct" className="w-full bg-black/40 border border-white/10 rounded p-2 text-sm text-white" /></div>
                <div><label className="block text-xs text-white/50 mb-1">API Base URL</label><input type="text" value={newNim.apiBase} onChange={e => setNewNim({...newNim, apiBase: e.target.value})} className="w-full bg-black/40 border border-white/10 rounded p-2 text-sm text-white" /></div>
                <div><label className="block text-xs text-white/50 mb-1">API Key</label><input type="password" value={newNim.apiKey} onChange={e => setNewNim({...newNim, apiKey: e.target.value})} placeholder="nvapi-..." className="w-full bg-black/40 border border-white/10 rounded p-2 text-sm text-white" /></div>
                <div><label className="block text-xs text-white/50 mb-1">Channel ID (IAEdu) - Opcional</label><input type="text" value={newNim.channelId} onChange={e => setNewNim({...newNim, channelId: e.target.value})} placeholder="Ex: cmp1fijefb030lx01mwi3ef5p" className="w-full bg-black/40 border border-white/10 rounded p-2 text-sm text-white" /></div>
                <button onClick={handleAddNimProfile} className="w-full bg-accent text-white rounded p-2 mt-2 font-semibold hover:bg-accent/80 transition">Guardar Perfil</button>
              </div>
            </div>
          </div>
        )}

        {/* Memory Modal */}
        {showMemoryModal && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="glass-panel w-full max-w-4xl p-6 relative flex flex-col max-h-[90vh]">
              <button onClick={() => setShowMemoryModal(false)} className="absolute top-4 right-4 text-white/50 hover:text-white"><X size={20} /></button>
              <h2 className="text-lg font-bold mb-2 flex items-center gap-2"><Brain className="text-accent"/> Memória Vetorial (ChromaDB)</h2>
              <p className="text-sm text-white/60 mb-4">A informação guardada aqui será sempre procurada pelo Specter quando fizeres uma pergunta relacionada.</p>
              
              <div className="flex gap-6 h-full min-h-[400px] max-h-full overflow-hidden">
                <div className="flex-1 flex flex-col">
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-accent mb-2">Adicionar Nova</h3>
                  <textarea 
                    value={memoryText} 
                    onChange={e => setMemoryText(e.target.value)} 
                    placeholder="O que queres que o Specter memorize permanentemente?" 
                    className="w-full flex-1 bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-white focus:border-accent outline-none resize-none mb-3" 
                  />
                  <button onClick={handleAddMemory} className="w-full flex items-center justify-center gap-2 bg-accent text-white rounded-lg p-3 font-semibold hover:bg-accent/80 transition shadow-[0_0_15px_rgba(6,182,212,0.3)] shrink-0">
                    <Save size={18} /> Gravar no ChromaDB
                  </button>
                </div>
                
                <div className="flex-1 flex flex-col border-l border-white/10 pl-6">
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-accent mb-2">Memórias Atuais ({memories.length})</h3>
                  <div className="flex-1 overflow-y-auto space-y-2 pr-2">
                    {memories.length === 0 ? (
                      <div className="text-center text-white/40 text-sm py-10">O banco de memória está vazio.</div>
                    ) : (
                      memories.map(mem => (
                        <div key={mem.id} className="bg-white/5 border border-white/10 rounded-lg p-3 group relative">
                          <p className="text-sm text-white/80 whitespace-pre-wrap">{mem.document}</p>
                          {mem.metadata && mem.metadata.date && (
                            <div className="text-[10px] text-white/30 mt-2 text-right">{new Date(mem.metadata.date).toLocaleString()}</div>
                          )}
                          <button 
                            onClick={() => handleDeleteMemory(mem.id)}
                            className="absolute top-2 right-2 p-1.5 bg-red-500/20 text-red-400 hover:bg-red-500/40 rounded opacity-0 group-hover:opacity-100 transition"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Skills Modal */}
        {showSkillsModal && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="glass-panel w-full max-w-5xl p-6 relative flex flex-col max-h-[90vh]">
              <button onClick={() => setShowSkillsModal(false)} className="absolute top-4 right-4 text-white/50 hover:text-white"><X size={20} /></button>
              <h2 className="text-lg font-bold mb-2 flex items-center gap-2"><Wrench className="text-accent"/> Gestor de Skills Modulares</h2>
              <p className="text-sm text-white/60 mb-6">Muda skills da Library para o teu Loadout para permitires que o Specter as use. Só as que estiverem ativas no Loadout serão processadas.</p>
              
              <div className="flex gap-6 h-full min-h-[500px] max-h-full overflow-hidden">
                {/* Available Skills (Library) */}
                <div className="flex-1 flex flex-col">
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-accent mb-4 border-b border-white/10 pb-2">Available Skills (Library)</h3>
                  <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                    {skills.filter(s => !s.in_loadout).length === 0 ? (
                      <div className="text-center text-white/40 py-8 text-sm">Não há skills disponíveis ou todas já estão no Loadout.</div>
                    ) : (
                      skills.filter(s => !s.in_loadout).map((skill, i) => (
                        <div key={i} className="bg-black/30 border border-white/5 rounded-lg p-4 hover:border-white/10 transition-colors">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-mono text-white/70 text-sm">{skill.name}</span>
                            <button 
                              onClick={() => handleUpdateSkillState(skill.name, true, true)}
                              className="text-xs px-2 py-1 rounded bg-white/5 text-white/60 hover:bg-white/10 hover:text-white transition flex items-center gap-1"
                            >
                              <Plus size={12} /> Add to Loadout
                            </button>
                          </div>
                          <p className="text-xs text-white/40">{skill.description}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
                
                {/* Active Loadout */}
                <div className="flex-1 flex flex-col border-l border-white/10 pl-6 relative">
                  <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-2">
                    <h3 className="text-xs font-semibold uppercase tracking-widest text-accent flex items-center gap-2">
                      Skills Being Used ({skills.filter(s => s.in_loadout).length})
                    </h3>
                    <div className="flex items-center gap-2">
                      <button 
                        onClick={() => {
                          const toUpdate = skills.filter(s => s.in_loadout).map(s => ({ ...s, enabled: true }));
                          handleBulkUpdateSkills(toUpdate);
                        }}
                        className="text-[10px] uppercase tracking-wider px-2 py-1 rounded border border-accent/30 text-accent hover:bg-accent/10 transition"
                      >
                        Enable All
                      </button>
                      <button 
                        onClick={() => {
                          const toUpdate = skills.filter(s => s.in_loadout).map(s => ({ ...s, enabled: false }));
                          handleBulkUpdateSkills(toUpdate);
                        }}
                        className="text-[10px] uppercase tracking-wider px-2 py-1 rounded border border-white/10 text-white/40 hover:bg-white/5 transition"
                      >
                        Disable All
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                    {skills.filter(s => s.in_loadout).length === 0 ? (
                      <div className="text-center text-white/40 py-8 text-sm">Nenhuma skill no Loadout.</div>
                    ) : (
                      skills.filter(s => s.in_loadout).map((skill, i) => (
                        <div key={i} className={`bg-black/40 border ${skill.enabled ? 'border-accent/40 shadow-[0_0_15px_rgba(6,182,212,0.1)]' : 'border-white/5 opacity-60'} rounded-lg p-4 transition-all duration-300 relative group`}>
                          
                          <button 
                            onClick={() => handleUpdateSkillState(skill.name, false, false)}
                            className="absolute top-2 right-2 p-1.5 bg-red-500/10 text-red-400 hover:bg-red-500/30 rounded opacity-0 group-hover:opacity-100 transition"
                            title="Remove from Loadout"
                          >
                            <Trash2 size={12} />
                          </button>
                          
                          <div className="flex items-center justify-between mb-2 pr-8">
                            <span className={`font-mono text-sm ${skill.enabled ? 'text-accent' : 'text-white/60'}`}>{skill.name}</span>
                            <button 
                              onClick={() => handleUpdateSkillState(skill.name, !skill.enabled, true)}
                              className={`text-xs px-3 py-1 rounded transition ${skill.enabled ? 'bg-accent text-white shadow-[0_0_10px_rgba(6,182,212,0.3)]' : 'bg-white/10 text-white/50 hover:bg-white/20'}`}
                            >
                              {skill.enabled ? 'ON' : 'OFF'}
                            </button>
                          </div>
                          <p className={`text-xs ${skill.enabled ? 'text-white/80' : 'text-white/40'}`}>{skill.description}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-4 sm:p-8 space-y-6 flex flex-col">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center -mt-16">
              <div className="mb-6 flex flex-col items-center">
                <img src="/SpecterApp.png?v=2" alt="Specter App" className="h-64 opacity-90 object-contain drop-shadow-[0_0_30px_rgba(6,182,212,0.3)]" />
              </div>
              <p className="text-white/50 text-sm mb-8 font-mono italic">{settingsMotto}</p>
              <p className="text-white/30 text-xs font-mono bg-white/5 px-4 py-2 rounded-lg border border-white/10 shadow-sm max-w-md text-center">
                Tip: Ativa o modo "Agent" na barra inferior para o Specter poder invocar as tuas Skills de forma autónoma.
              </p>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6 w-full pb-8">
              {messages.map((msg, i) => {
                if (msg.role === 'assistant' && msg.content === '' && !isLoading && i === messages.length - 1) {
                  return (
                    <div key={i} className="flex gap-4 justify-start">
                      <div className="w-8 h-8 shrink-0 mt-2 flex items-center justify-center animate-pulse">
                        <img src="/iconSpecterApp.png" alt="Specter" className="w-full h-full object-contain drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
                      </div>
                        <div className="glass-panel rounded-2xl rounded-tl-sm px-5 py-3 w-fit flex items-center justify-center">
                          <span className="text-sm text-white/50 animate-pulse font-medium">a escrever...</span>
                        </div>
                    </div>
                  )
                }
              if (msg.role === 'assistant' && msg.content === '') return null;

              return (
                <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role !== 'user' && (
                    <div className={`w-8 h-8 shrink-0 flex items-center justify-center mt-2 ${msg.role === 'system' ? 'rounded-full border bg-red-500/10 border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.3)]' : ''}`}>
                      {msg.role === 'system' ? <Settings size={16} className="text-red-400" /> : <img src="/iconSpecterApp.png" alt="Specter" className="w-full h-full object-contain drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />}
                    </div>
                  )}
                  
                  {msg.role === 'user' ? (
                    <div className="flex flex-col items-end gap-1.5 max-w-[85%]">
                      {msg.content.includes('[Conteúdo do Ficheiro Anexado:') && (
                        <div className="bg-white/10 border border-white/10 text-white/70 text-xs px-3 py-1.5 rounded-lg flex items-center gap-2">
                          <span className="font-medium">📎 {msg.content.match(/\[Conteúdo do Ficheiro Anexado: (.+?)\]/)?.[1] || 'Ficheiro Anexado'}</span>
                        </div>
                      )}
                      <div className="bg-white text-black rounded-2xl rounded-tr-sm shadow-xl px-5 py-3">
                        <p className="whitespace-pre-wrap leading-relaxed">
                          {msg.content.replace(/\[Conteúdo do Ficheiro Anexado: .+?\]\n```\n[\s\S]*?\n```\n\n/, '')}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className={`max-w-[85%] rounded-2xl px-5 py-3 group ${
                      msg.role === 'system'
                        ? 'bg-red-500/10 text-red-200 border border-red-500/20 rounded-tl-sm text-sm'
                        : 'glass-panel rounded-tl-sm w-full'
                    }`}>
                      {(msg.name || msg.agentRole) && (
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10 text-xs">
                          {msg.name && <span className="font-bold text-accent">{msg.name}</span>}
                          {msg.agentRole && <span className="px-2 py-0.5 bg-white/10 rounded-full text-white/70">{msg.agentRole}</span>}
                        </div>
                      )}
                      <div className="prose prose-invert max-w-none text-sm leading-relaxed prose-pre:p-0 prose-pre:bg-transparent">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ code: CodeBlock }}>
                          {msg.content.replace(/```(?:json)?\s*\{\s*"name"\s*:[\s\S]*?"arguments"\s*:[\s\S]*?\}\s*```/g, '').replace(/^\s*\{\s*"name"\s*:[\s\S]*?"arguments"\s*:[\s\S]*?\}\s*$/g, '')}
                        </ReactMarkdown>
                      </div>
                      
                      {msg.role !== 'system' && (
                        <div className="flex items-center justify-end mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <MessageCopyButton content={msg.content} />
                        </div>
                      )}
                    </div>
                  )}

                  {msg.role === 'user' && (
                    <div className="w-8 h-8 shrink-0 rounded-full bg-white/10 flex items-center justify-center border border-white/20 mt-2">
                      <User size={16} />
                    </div>
                  )}
                </div>
              )
            })}
            
                {isLoading && (
                  <div className="flex gap-4 justify-start">
                    <div className="w-8 h-8 shrink-0 mt-2 flex items-center justify-center animate-pulse">
                      <img src="/iconSpecterApp.png" alt="Specter" className="w-full h-full object-contain drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
                    </div>
                    <div className="glass-panel rounded-2xl rounded-tl-sm px-5 py-3 flex flex-col items-center justify-center w-fit">
                      <span className="text-sm text-white/50 animate-pulse font-medium">a escrever...</span>
                      {activeMode === 'local' && <span className="text-[10px] text-accent/60 uppercase tracking-widest mt-1">Motor Local...</span>}
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 sm:p-8 sm:pb-12 z-10 w-full">
          <div className="max-w-4xl mx-auto relative">
            <div className="bg-[#15171a] border border-white/5 rounded-2xl flex flex-col pt-3 pb-2 px-3 shadow-2xl relative">
              
              {/* Attached File Badge */}
              {attachedFile && (
                <div className="flex items-center mb-2 px-2 mt-1">
                  <div className="bg-accent/20 border border-accent/30 text-accent text-xs px-3 py-1.5 rounded-full flex items-center gap-2">
                    <span className="truncate max-w-[200px]">{attachedFile.name}</span>
                    <button onClick={() => setAttachedFile(null)} className="hover:text-white transition"><X size={12} /></button>
                  </div>
                </div>
              )}

              {/* Input Text Area and Model Selector */}
              <div className="flex relative items-start">
                <textarea 
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Message Specter ..."
                  className="w-full bg-transparent resize-none overflow-y-auto text-sm text-white focus:outline-none placeholder:text-white/30 h-[60px] pl-2"
                />
                
                {/* Floating Model Selector Popover */}
                {showModelSelector && (
                  <div className="absolute right-0 bottom-full mb-3 w-80 bg-[#1a1d21] border border-white/10 rounded-xl shadow-2xl p-4 z-50">
                    <div className="flex items-center justify-between mb-3 border-b border-white/5 pb-2">
                      <h3 className="text-sm font-medium text-white/80">Select Model</h3>
                      <button onClick={() => setShowModelSelector(false)} className="text-white/40 hover:text-white"><X size={14}/></button>
                    </div>
                    
                    {chatMode === 'swarm' ? (
                      <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                        <div className="text-xs text-white/50 mb-2">Selecione os modelos para a equipa Swarm:</div>
                        {nimProfiles.map(p => (
                          <label key={p.id} className="flex items-center gap-2 text-xs text-white p-2 bg-black/20 rounded hover:bg-white/5 cursor-pointer">
                            <input type="checkbox" checked={swarmSelectedIds.includes(p.id)} onChange={(e) => {
                              if (e.target.checked) setSwarmSelectedIds(prev => [...prev, p.id])
                              else setSwarmSelectedIds(prev => prev.filter(id => id !== p.id))
                            }} />
                            <span className="truncate">{p.name}</span>
                            <span className="ml-auto text-[10px] text-accent/50">NIM</span>
                          </label>
                        ))}
                        {localModels.map(m => (
                          <label key={m} className="flex items-center gap-2 text-xs text-white p-2 bg-black/20 rounded hover:bg-white/5 cursor-pointer">
                            <input type="checkbox" checked={swarmSelectedIds.includes(m)} onChange={(e) => {
                              if (e.target.checked) setSwarmSelectedIds(prev => [...prev, m])
                              else setSwarmSelectedIds(prev => prev.filter(id => id !== m))
                            }} />
                            <span className="truncate">{m.split(/[\\/]/).pop()}</span>
                            <span className="ml-auto text-[10px] text-accent/50">Local</span>
                          </label>
                        ))}
                        {swarmSelectedIds.length === 0 && (
                          <div className="text-[10px] text-orange-400/80 mt-2">Nenhum selecionado. Todos os modelos serão usados por defeito.</div>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-4">
                      {/* Local Models */}
                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-xs font-semibold text-accent/80 uppercase tracking-wider flex items-center gap-1.5"><Database size={12}/> Local</span>
                          <button onClick={() => setActiveMode('local')} className={`text-[10px] px-2 py-0.5 rounded transition ${activeMode === 'local' ? 'bg-accent text-white' : 'bg-white/5 text-white/40 hover:bg-white/10'}`}>Ativar</button>
                        </div>
                        <div className="flex items-center gap-2 mb-2 w-full">
                          <select className="flex-1 min-w-0 bg-black/40 border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-accent truncate" value={activeLocalModel} onChange={(e) => setActiveLocalModel(e.target.value)}>
                            {localModels.length === 0 && <option value="">Nenhum modelo...</option>}
                            {localModels.map(path => {
                              const name = path.split(/[\\/]/).pop() || path;
                              const shortName = name.length > 35 ? name.substring(0, 15) + '...' + name.substring(name.length - 15) : name;
                              return <option key={path} value={path}>{shortName}</option>
                            })}
                          </select>
                          {localModels.length > 0 && (
                            <button 
                              onClick={() => {
                                const newModels = localModels.filter(m => m !== activeLocalModel)
                                setLocalModels(newModels)
                                setActiveLocalModel(newModels[0] || '')
                              }}
                              className="p-2 border border-white/10 rounded-lg text-red-400/50 hover:bg-red-500/20 hover:text-red-400 transition shrink-0"
                              title="Remover da lista"
                            >
                              <Trash2 size={14} />
                            </button>
                          )}
                        </div>
                        <button onClick={handleAddLocalModel} className="w-full text-xs py-1.5 border border-white/10 border-dashed rounded-lg text-white/50 hover:bg-white/5 hover:text-white transition flex justify-center items-center gap-1"><Plus size={12}/> Add Local</button>
                      </div>

                      {/* NIM Models */}
                      <div>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-xs font-semibold text-accent/80 uppercase tracking-wider flex items-center gap-1.5"><Cloud size={12}/> NIM / Cloud</span>
                          <button onClick={() => setActiveMode('nim')} className={`text-[10px] px-2 py-0.5 rounded transition ${activeMode === 'nim' ? 'bg-accent text-white' : 'bg-white/5 text-white/40 hover:bg-white/10'}`}>Ativar</button>
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                          <select className="flex-1 bg-black/40 border border-white/10 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-accent" value={activeNimId} onChange={(e) => setActiveNimId(e.target.value)}>
                            {nimProfiles.length === 0 && <option value="">Nenhum perfil...</option>}
                            {nimProfiles.map(prof => <option key={prof.id} value={prof.id}>{prof.name}</option>)}
                          </select>
                          {nimProfiles.length > 0 && (
                            <button 
                              onClick={() => {
                                const newProfs = nimProfiles.filter(p => p.id !== activeNimId)
                                setNimProfiles(newProfs)
                                setActiveNimId(newProfs[0]?.id || '')
                              }}
                              className="p-2 border border-white/10 rounded-lg text-red-400/50 hover:bg-red-500/20 hover:text-red-400 transition"
                              title="Remover perfil"
                            >
                              <Trash2 size={14} />
                            </button>
                          )}
                        </div>
                        <button onClick={() => setShowNimModal(true)} className="w-full text-xs py-1.5 border border-white/10 border-dashed rounded-lg text-white/50 hover:bg-white/5 hover:text-white transition flex justify-center items-center gap-1"><Plus size={12}/> Add NIM</button>
                      </div>
                      </div>
                    )}
                  </div>
                )}

              </div>

              {/* Bottom Actions Bar */}
              <div className="flex items-center justify-between mt-2">
                
                {/* Left side actions */}
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => setShowModelSelector(!showModelSelector)}
                    className="h-8 px-2.5 rounded-lg bg-white/5 text-white/50 hover:text-white hover:bg-white/10 transition flex items-center justify-center gap-1.5"
                    title="Selecionar Modelo"
                  >
                    {chatMode === 'swarm' ? <Brain size={13} className="text-accent" /> : activeMode === 'local' ? <Database size={13} className="text-accent" /> : <Cloud size={13} className="text-accent" />}
                    <span className="text-xs font-medium font-mono truncate max-w-[120px]">
                      {chatMode === 'swarm'
                        ? `Swarm (${swarmSelectedIds.length || localModels.length + nimProfiles.length})`
                        : activeMode === 'local' 
                        ? activeLocalModel.split(/[\\/]/).pop() || 'No Model'
                        : nimProfiles.find(p => p.id === activeNimId)?.name || 'No NIM'}
                    </span>
                    <ChevronUp size={12} />
                  </button>
                  <div className="w-px h-4 bg-white/10 mx-1"></div>
                  <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="h-8 px-2.5 rounded-lg bg-white/5 text-white/50 hover:text-white hover:bg-white/10 transition flex items-center justify-center gap-1.5"
                    title="Anexar Ficheiro de Texto"
                  >
                    <ChevronUp size={14} />
                    <span className="text-xs font-medium">Files</span>
                  </button>
                  <button 
                    onClick={() => setIsSearchEnabled(!isSearchEnabled)}
                    className={`h-8 px-2.5 rounded-lg transition flex items-center justify-center gap-1.5 ${isSearchEnabled ? 'bg-accent/20 text-accent' : 'bg-white/5 text-white/50 hover:text-white hover:bg-white/10'}`}
                    title="Ativar Pesquisa Web Forçada"
                  >
                    <Search size={13} />
                    <span className="text-xs font-medium">Web Search</span>
                  </button>
                  <button 
                    onClick={() => setIsTerminalEnabled(!isTerminalEnabled)}
                    className={`h-8 px-2.5 rounded-lg transition flex items-center justify-center gap-1.5 ${isTerminalEnabled ? 'bg-red-500/20 text-red-400' : 'bg-white/5 text-white/50 hover:text-white hover:bg-white/10'}`}
                    title="Ativar Permissão de Comandos de Terminal"
                  >
                    <Terminal size={13} />
                    <span className="text-xs font-medium">Terminal</span>
                  </button>
                </div>

                {/* Right side actions */}
                <div className="flex items-center gap-3">
                  
                  {/* Agent | Chat | Swarm Toggle */}
                  <div className="flex items-center bg-black/40 rounded-full p-1 border border-white/5">
                    <button 
                      onClick={() => setChatMode('swarm')}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition flex items-center gap-1 ${chatMode === 'swarm' ? 'bg-accent text-white shadow-sm' : 'text-white/40 hover:text-white/70'}`}
                    >
                      Swarm
                    </button>
                    <button 
                      onClick={() => setChatMode('agent')}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition ${chatMode === 'agent' ? 'bg-white/10 text-white shadow-sm' : 'text-white/40 hover:text-white/70'}`}
                    >
                      Agent
                    </button>
                    <button 
                      onClick={() => setChatMode('chat')}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition ${chatMode === 'chat' ? 'bg-white/10 text-white shadow-sm' : 'text-white/40 hover:text-white/70'}`}
                    >
                      Chat
                    </button>
                  </div>

                  {/* Send Button */}
                  {(isLoading || isStreaming) ? (
                    <button 
                      onClick={handleStop}
                      className="w-8 h-8 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/40 border border-red-500/30 transition flex items-center justify-center"
                    >
                      <Square size={14} className="fill-current" />
                    </button>
                  ) : (
                    <button 
                      onClick={handleSend}
                      disabled={!input.trim() && messages[messages.length-1]?.role !== 'assistant'}
                      className="w-8 h-8 rounded-xl bg-accent/20 text-accent hover:bg-accent hover:text-white border border-accent/30 disabled:opacity-50 transition flex items-center justify-center shadow-[0_0_10px_rgba(6,182,212,0.15)]"
                    >
                      <ArrowUp size={16} />
                    </button>
                  )}
                </div>

              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
