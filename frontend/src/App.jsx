import { useState, useRef, useEffect } from 'react'
import { Send, FileText, Bot, User, Loader2, UploadCloud, CheckCircle, XCircle } from 'lucide-react'

function App() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'System online. How can I assist you today?' }
  ])
  const [isLoading, setIsLoading] = useState(false)
  
  const [file, setFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')

  // Auto-scroll to bottom of chat
  const messagesEndRef = useRef(null)
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleFileUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setIsUploading(true)
    setUploadStatus('Uploading PDF...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Upload failed')
      
      // Explicit success message
      setUploadStatus('PDF successfully uploaded!')
      setTimeout(() => setUploadStatus(''), 5000) 
      setFile(null) 
      
      // Automatically clear the chat history for the new document
      setMessages([
        { role: 'assistant', content: 'New document loaded. What would you like to know about it?' }
      ])
      
    } catch (error) {
      setUploadStatus('Upload failed')
      setTimeout(() => setUploadStatus(''), 5000) 
    } finally {
      setIsUploading(false)
    }
  }

  const handleAskQuestion = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    // 1. Add user message AND an empty assistant message to act as a placeholder
    const newMessages = [...messages, { role: 'user', content: query }]
    setMessages([...newMessages, { role: 'assistant', content: '' }])
    setQuery('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query, chat_history: messages }),
      })

      if (!response.ok) throw new Error('Network response was not ok')

      // 2. Open the stream reader
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let done = false
      let streamedText = ''

      // 3. Loop through the chunks as they arrive from FastAPI
      while (!done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        
        if (value) {
          // Decode the raw bytes into text
          streamedText += decoder.decode(value, { stream: true })
          
          // Dynamically update the last message in the UI
          setMessages((prev) => {
            const updatedMessages = [...prev]
            updatedMessages[updatedMessages.length - 1].content = streamedText
            return updatedMessages
          })
        }
      }
    } catch (error) {
      setMessages((prev) => {
        const updatedMessages = [...prev]
        updatedMessages[updatedMessages.length - 1].content = 'Error connecting to the RAG engine.'
        return updatedMessages
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen w-full bg-[#1e1e22] font-sans text-gray-200">
      
      {/* TOP NAVBAR (Minimalist Upload) */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-[#1e1e22]/80 backdrop-blur-md z-10 sticky top-0">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
          <h1 className="font-medium text-gray-300 tracking-wide text-sm">RAG_ENGINE_V1</h1>
        </div>

        <form onSubmit={handleFileUpload} className="flex items-center gap-3">
          {uploadStatus && (
            <span className={`text-xs font-medium ${uploadStatus === 'Upload failed' ? 'text-red-400' : 'text-emerald-400'} flex items-center gap-1 mr-2`}>
              {uploadStatus === 'PDF successfully uploaded!' && <CheckCircle className="w-4 h-4" />}
              {uploadStatus === 'Upload failed' && <XCircle className="w-4 h-4" />}
              {uploadStatus}
            </span>
          )}
          
          <label className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-gray-700 bg-gray-800/50 hover:bg-gray-700 text-sm cursor-pointer transition-colors text-gray-300">
            <UploadCloud className="w-4 h-4 text-gray-400" />
            <span className="truncate max-w-[150px]">{file ? file.name : "Select PDF"}</span>
            <input 
              type="file" 
              className="hidden" 
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])} 
            />
          </label>
          
          <button 
            type="submit" 
            disabled={isUploading || !file} 
            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-500 text-white text-sm rounded-md transition-colors flex items-center gap-2"
          >
            {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            Upload
          </button>
        </form>
      </header>

      {/* CHAT AREA */}
      <main className="flex-1 overflow-y-auto scroll-smooth pb-32">
        <div className="max-w-3xl mx-auto flex flex-col pt-8">
          {messages.map((msg, index) => (
            <div key={index} className={`w-full ${msg.role === 'user' ? 'bg-[#1e1e22]' : 'bg-[#25252b]'} border-b border-gray-800/50`}>
              <div className="max-w-3xl mx-auto flex gap-6 px-4 py-8">
                
                <div className="flex-shrink-0 pt-1">
                  {msg.role === 'user' ? (
                    <div className="w-8 h-8 rounded-md bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
                      <User className="w-5 h-5 text-indigo-400" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-md bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                      <Bot className="w-5 h-5 text-emerald-400" />
                    </div>
                  )}
                </div>

                <div className="flex-1 space-y-2 text-[15px] leading-relaxed text-gray-300">
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
                
              </div>
            </div>
          ))}
          
          {isLoading && messages[messages.length - 1].role === 'user' && (
            <div className="w-full bg-[#25252b] border-b border-gray-800/50">
              <div className="max-w-3xl mx-auto flex gap-6 px-4 py-8">
                <div className="flex-shrink-0 pt-1">
                  <div className="w-8 h-8 rounded-md bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                    <Bot className="w-5 h-5 text-emerald-400" />
                  </div>
                </div>
                <div className="flex items-center gap-3 text-gray-500">
                  <Loader2 className="w-5 h-5 animate-spin text-emerald-500/70" />
                  Analyzing knowledge base...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* FLOATING INPUT BOX */}
      <footer className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#1e1e22] via-[#1e1e22] to-transparent pt-12 pb-6 px-4">
        <div className="max-w-3xl mx-auto">
          <form 
            onSubmit={handleAskQuestion} 
            className="relative flex items-center bg-[#2d2d34] border border-gray-700 rounded-xl shadow-2xl focus-within:ring-2 focus-within:ring-indigo-500/50 transition-all overflow-hidden"
          >
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Message the RAG Engine..." 
              className="flex-1 w-full bg-transparent border-none py-4 pl-4 pr-14 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-0"
              disabled={isLoading}
            />
            <button 
              type="submit" 
              disabled={isLoading || !query.trim()} 
              className="absolute right-2 p-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-center mt-3">
            <span className="text-[11px] text-gray-500 font-medium tracking-wide">
              AI generated content may be inaccurate. Review documents independently.
            </span>
          </div>
        </div>
      </footer>

    </div>
  )
}

export default App