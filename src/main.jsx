import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { AnimatePresence, motion } from "motion/react";
import Hls from "hls.js";
import {
  ArrowRight,
  Check,
  CreditCard,
  Globe,
  LayoutDashboard,
  Lock,
  LogOut,
  Mail,
  Newspaper,
  Settings,
  Sparkles,
  User,
} from "lucide-react";
import "./index.css";

const VIDEO_URL =
  "https://stream.mux.com/kimF2ha9zLrX64H00UgLGPflCzNtl1T0215MlAmeOztv8.m3u8";

const defaultPrefs = {
  hours: 24,
  top_n: 10,
  profile_name: "default_ai_reader",
  use_llm: true,
  preferred_sources: ["OpenAI News", "Anthropic News", "TechCrunch AI"],
  preferred_kinds: ["article", "youtube_video"],
  keywords: ["openai", "anthropic", "agents", "llm"],
  excluded_keywords: [],
};

function BackgroundVideo() {
  const videoRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return undefined;
    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = VIDEO_URL;
      return undefined;
    }
    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(VIDEO_URL);
      hls.attachMedia(video);
      return () => hls.destroy();
    }
    return undefined;
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <video
        ref={videoRef}
        autoPlay
        muted
        loop
        playsInline
        className="w-full h-full object-cover opacity-100"
      />
      <div className="absolute inset-0 bg-black/55" />
    </div>
  );
}

function Navbar({ user, onOpenAuth, onDashboard, onLogout }) {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="relative z-20 px-6 py-6 w-full"
    >
      <div className="liquid-glass rounded-full px-6 py-3 flex items-center justify-between max-w-5xl mx-auto">
        <div className="flex items-center gap-8">
          <button
            className="flex items-center gap-2 cursor-pointer"
            onClick={onDashboard}
            type="button"
          >
            <Globe className="w-6 h-6 text-white" />
            <span className="text-white font-semibold text-lg">Asme</span>
          </button>
          <div className="hidden md:flex items-center gap-8 text-white/80 text-sm font-medium">
            {["Features", "Pricing", "About"].map((link) => (
              <a
                className="hover:text-white transition-colors duration-300"
                href={`#${link.toLowerCase()}`}
                key={link}
              >
                {link}
              </a>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <button
                type="button"
                className="text-white hover:text-white/80 transition-colors text-sm font-medium cursor-pointer"
                onClick={onDashboard}
              >
                Dashboard
              </button>
              <button
                type="button"
                className="liquid-glass rounded-full px-5 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity cursor-pointer"
                onClick={onLogout}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                className="text-white hover:text-white/80 transition-colors text-sm font-medium cursor-pointer"
                onClick={() => onOpenAuth("register")}
              >
                Sign Up
              </button>
              <button
                type="button"
                className="liquid-glass rounded-full px-6 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity cursor-pointer"
                onClick={() => onOpenAuth("login")}
              >
                Login
              </button>
            </>
          )}
        </div>
      </div>
    </motion.nav>
  );
}

function Hero({ onOpenAuth }) {
  const [showForm, setShowForm] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [placeholder, setPlaceholder] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    if (!showForm) return undefined;
    const text = submitted
      ? "You Will Receive Notifications By Email"
      : "Enter Your Email Here For Early Access";
    setPlaceholder("");
    let index = 0;
    const timer = window.setInterval(() => {
      setPlaceholder(text.slice(0, index + 1));
      index += 1;
      if (index >= text.length) window.clearInterval(timer);
    }, 60);
    return () => window.clearInterval(timer);
  }, [showForm, submitted]);

  useEffect(() => {
    if (!submitted) return undefined;
    const timer = window.setTimeout(() => {
      setSubmitted(false);
      setShowForm(false);
      setEmail("");
    }, 4000);
    return () => window.clearTimeout(timer);
  }, [submitted]);

  return (
    <section className="relative flex-1 flex flex-col items-center justify-center px-6">
      <div className="relative z-10 text-center max-w-5xl mx-auto flex flex-col items-center justify-center w-full gap-12">
        <div>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-white/80 text-[10px] md:text-[11px] font-medium tracking-[0.2em] uppercase mb-4"
          >
            BUILD A NO-CODE AI APP IN MINUTES
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            style={{ fontFamily: "'Instrument Serif', serif" }}
            className="text-4xl md:text-[64px] font-medium tracking-[-0.01em] leading-[1.1] mb-6 bg-gradient-to-b from-white via-white/95 to-white/70 bg-clip-text text-transparent max-w-4xl"
          >
            A new way to think and create
            <br className="hidden md:block" /> with computers
          </motion.h1>
          <p className="mx-auto max-w-2xl text-white/70 text-sm md:text-base leading-7">
            Register, set AI news priorities, rank digests, and subscribe to daily
            email updates from your own AI news engine.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="min-h-[50px] mt-2"
        >
          <AnimatePresence mode="wait">
            {!showForm ? (
              <motion.button
                key="button"
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="px-10 py-3 text-[14px] font-medium border border-white/10 rounded-full hover:border-white/30 hover:bg-white/[0.02] transition-all duration-300 text-white/90 backdrop-blur-sm cursor-pointer"
                type="button"
                onClick={() => setShowForm(true)}
              >
                Get early access
              </motion.button>
            ) : (
              <motion.form
                key="form"
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="flex items-center gap-2 pl-5 pr-1.5 py-1.5 text-[14px] font-medium border border-white/20 rounded-full bg-white/[0.02] backdrop-blur-sm w-full max-w-[320px] focus-within:border-white/40 transition-colors duration-300"
                onSubmit={(event) => {
                  event.preventDefault();
                  setSubmitted(true);
                  setTimeout(() => onOpenAuth("register", email), 600);
                }}
              >
                <input
                  autoFocus
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="bg-transparent outline-none text-white placeholder-white/45 flex-1 min-w-0"
                  placeholder={placeholder}
                  type="email"
                />
                <button
                  type="submit"
                  className="w-9 h-9 rounded-full bg-white text-black grid place-items-center"
                >
                  {submitted ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <ArrowRight className="w-4 h-4" />
                  )}
                </button>
              </motion.form>
            )}
          </AnimatePresence>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-white/80 hover:text-white/40 transition-colors duration-300 text-[13px] font-medium tracking-wide"
        >
          Play Video Demo
        </motion.div>
      </div>
    </section>
  );
}

function AuthModal({ mode, initialEmail, onClose, onAuth }) {
  const [isRegister, setIsRegister] = useState(mode !== "login");
  const [form, setForm] = useState({
    name: "Hassan",
    email: initialEmail || "",
    password: "",
  });
  const [error, setError] = useState("");

  useEffect(() => setIsRegister(mode !== "login"), [mode]);

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      const data = await api(`/api/auth/${isRegister ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify(form),
      });
      onAuth(data);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 px-4">
      <motion.form
        initial={{ opacity: 0, scale: 0.96, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="liquid-glass w-full max-w-md rounded-[28px] p-7"
        onSubmit={submit}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-white/50 text-xs uppercase tracking-[0.2em]">
              Account
            </p>
            <h2 className="text-2xl font-semibold">
              {isRegister ? "Create account" : "Login"}
            </h2>
          </div>
          <button className="text-white/60" onClick={onClose} type="button">
            Close
          </button>
        </div>
        <div className="grid gap-4">
          {isRegister && (
            <Field
              icon={User}
              label="Name"
              value={form.name}
              onChange={(name) => setForm({ ...form, name })}
            />
          )}
          <Field
            icon={Mail}
            label="Email"
            value={form.email}
            type="email"
            onChange={(email) => setForm({ ...form, email })}
          />
          <Field
            icon={Lock}
            label="Password"
            value={form.password}
            type="password"
            onChange={(password) => setForm({ ...form, password })}
          />
        </div>
        {error && <p className="mt-4 text-sm text-red-300">{error}</p>}
        <button
          className="mt-6 w-full rounded-full bg-white text-black py-3 font-semibold"
          type="submit"
        >
          {isRegister ? "Register" : "Login"}
        </button>
        <button
          className="mt-4 w-full text-center text-white/60 text-sm"
          type="button"
          onClick={() => setIsRegister(!isRegister)}
        >
          {isRegister ? "Already have an account? Login" : "Need an account? Register"}
        </button>
      </motion.form>
    </div>
  );
}

function Dashboard({ user, token, onLogout, onUser }) {
  const [page, setPage] = useState("preferences");
  const [prefs, setPrefs] = useState(user.preferences || defaultPrefs);
  const [digests, setDigests] = useState(null);
  const [message, setMessage] = useState("");

  async function savePrefs() {
    setMessage("Saving preferences...");
    try {
      const data = await api("/api/preferences", {
        method: "POST",
        token,
        body: JSON.stringify(prefs),
      });
      setPrefs({ ...prefs, ...data.preferences });
      setMessage("Preferences saved.");
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function loadDigests() {
    setMessage("Loading ranked digests...");
    try {
      const data = await api("/api/dashboard/digests", {
        method: "POST",
        token,
        body: JSON.stringify(prefs),
      });
      setDigests(data);
      setPage("digests");
      setMessage(`${data.ranking_method.toUpperCase()} ranking returned ${data.total_items} items.`);
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function startCheckout() {
    setMessage("Opening Stripe Checkout...");
    try {
      const data = await api("/api/payments/checkout", {
        method: "POST",
        body: JSON.stringify({ name: user.name, email: user.email }),
      });
      window.location.href = data.url;
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <main className="min-h-screen bg-[#050505] text-white dashboard-grid">
      <aside className="border-r border-white/10 p-5">
        <div className="flex items-center gap-2 mb-8">
          <Globe className="w-6 h-6" />
          <span className="font-semibold text-lg">Asme</span>
        </div>
        <nav className="grid gap-2">
          <NavButton icon={Settings} active={page === "preferences"} onClick={() => setPage("preferences")}>Priorities</NavButton>
          <NavButton icon={Newspaper} active={page === "digests"} onClick={() => setPage("digests")}>Digest maker</NavButton>
          <NavButton icon={CreditCard} active={page === "subscription"} onClick={() => setPage("subscription")}>Subscription</NavButton>
        </nav>
        <button
          type="button"
          className="mt-8 flex items-center gap-2 text-white/50 hover:text-white"
          onClick={onLogout}
        >
          <LogOut className="w-4 h-4" /> Logout
        </button>
      </aside>
      <section className="p-5 md:p-8 overflow-auto">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <p className="text-white/50 text-sm">Logged in as {user.email}</p>
            <h1 className="text-3xl font-semibold">AI news dashboard</h1>
          </div>
          <div className="glass-pill px-4 py-2 text-sm text-white/75">
            {user.subscription_status || "free"} plan
          </div>
        </div>
        {message && <div className="mb-5 rounded-2xl bg-white/5 border border-white/10 p-4 text-sm text-white/75">{message}</div>}
        {page === "preferences" && (
          <Preferences prefs={prefs} setPrefs={setPrefs} onSave={savePrefs} onRun={loadDigests} />
        )}
        {page === "digests" && (
          <DigestMaker prefs={prefs} setPrefs={setPrefs} onRun={loadDigests} digests={digests} />
        )}
        {page === "subscription" && (
          <Subscription user={user} onCheckout={startCheckout} />
        )}
      </section>
    </main>
  );
}

function Preferences({ prefs, setPrefs, onSave, onRun }) {
  return (
    <Panel title="Enter your priorities" description="Save what this user wants the ranking agent to prefer.">
      <div className="grid md:grid-cols-2 gap-4">
        <Select label="Profile" value={prefs.profile_name} onChange={(profile_name) => setPrefs({ ...prefs, profile_name })} options={[
          ["default_ai_reader", "Default AI reader"],
          ["openai_anthropic", "OpenAI + Anthropic"],
          ["builders", "Builders"],
        ]} />
        <Toggle label="Use LLM ranking" checked={prefs.use_llm} onChange={(use_llm) => setPrefs({ ...prefs, use_llm })} />
        <TextArea label="Preferred sources" value={toCsv(prefs.preferred_sources)} onChange={(value) => setPrefs({ ...prefs, preferred_sources: fromCsv(value) })} />
        <TextArea label="Keywords" value={toCsv(prefs.keywords)} onChange={(value) => setPrefs({ ...prefs, keywords: fromCsv(value) })} />
        <TextArea label="Content types" value={toCsv(prefs.preferred_kinds)} onChange={(value) => setPrefs({ ...prefs, preferred_kinds: fromCsv(value) })} />
        <TextArea label="Exclude keywords" value={toCsv(prefs.excluded_keywords)} onChange={(value) => setPrefs({ ...prefs, excluded_keywords: fromCsv(value) })} />
      </div>
      <div className="flex gap-3 mt-6">
        <button className="rounded-full bg-white text-black px-5 py-3 font-semibold" onClick={onSave} type="button">Save priorities</button>
        <button className="rounded-full border border-white/15 px-5 py-3 font-semibold" onClick={onRun} type="button">Generate digest</button>
      </div>
    </Panel>
  );
}

function DigestMaker({ prefs, setPrefs, onRun, digests }) {
  return (
    <div className="grid gap-5">
      <Panel title="Digest making" description="Choose the lookback window and number of ranked articles.">
        <div className="grid md:grid-cols-3 gap-4">
          <Field label="Last hours" type="number" value={prefs.hours} onChange={(hours) => setPrefs({ ...prefs, hours: Number(hours) })} />
          <Field label="Top articles" type="number" value={prefs.top_n} onChange={(top_n) => setPrefs({ ...prefs, top_n: Number(top_n) })} />
          <Toggle label="Use LLM ranking" checked={prefs.use_llm} onChange={(use_llm) => setPrefs({ ...prefs, use_llm })} />
        </div>
        <button className="mt-5 rounded-full bg-white text-black px-5 py-3 font-semibold" onClick={onRun} type="button">Get top digests</button>
      </Panel>
      {digests && (
        <div className="grid gap-3">
          <p className="text-white/60 text-sm">Ranking: {digests.ranking_method} | Window: {digests.lookback_hours} hours</p>
          {digests.items.map((item) => (
            <article className="rounded-3xl border border-white/10 bg-white/[0.04] p-5" key={item.identity_key}>
              <div className="flex justify-between gap-4">
                <h3 className="font-semibold text-lg">{item.rank}. {item.title}</h3>
                <span className="text-white/50 text-sm">{item.score}</span>
              </div>
              <p className="mt-2 text-white/70 leading-7">{item.summary}</p>
              <a className="mt-3 inline-block text-white/80 text-sm" href={item.url} target="_blank" rel="noreferrer">Open source</a>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function Subscription({ user, onCheckout }) {
  return (
    <Panel title="Subscription" description="Subscribe to receive daily AI digest emails for the last 24 hours.">
      <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 max-w-xl">
        <Sparkles className="w-8 h-8 mb-4 text-white" />
        <h3 className="text-xl font-semibold">Daily AI digest email</h3>
        <p className="mt-2 text-white/65 leading-7">
          Stripe Checkout collects payment details securely. In test mode, use fake cards. In setup mode at $0.00, the card is saved without charge.
        </p>
        <div className="mt-5 text-sm text-white/60">Account: {user.email}</div>
        <button className="mt-6 rounded-full bg-white text-black px-6 py-3 font-semibold" onClick={onCheckout} type="button">Try payment</button>
      </div>
    </Panel>
  );
}

function Panel({ title, description, children }) {
  return (
    <section className="rounded-[30px] border border-white/10 bg-white/[0.035] p-6">
      <h2 className="text-2xl font-semibold">{title}</h2>
      <p className="mt-2 mb-6 text-white/55">{description}</p>
      {children}
    </section>
  );
}

function Field({ label, value, onChange, type = "text", icon: Icon }) {
  return (
    <label className="grid gap-2 text-sm text-white/60">
      {label}
      <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-black/30 px-3">
        {Icon && <Icon className="w-4 h-4 text-white/40" />}
        <input
          className="w-full bg-transparent py-3 outline-none text-white"
          type={type}
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
      </div>
    </label>
  );
}

function TextArea({ label, value, onChange }) {
  return (
    <label className="grid gap-2 text-sm text-white/60">
      {label}
      <textarea
        className="min-h-[96px] rounded-2xl border border-white/10 bg-black/30 p-3 outline-none text-white"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function Select({ label, value, onChange, options }) {
  return (
    <label className="grid gap-2 text-sm text-white/60">
      {label}
      <select
        className="rounded-2xl border border-white/10 bg-black/80 p-3 outline-none text-white"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map(([id, text]) => <option key={id} value={id}>{text}</option>)}
      </select>
    </label>
  );
}

function Toggle({ label, checked, onChange }) {
  return (
    <label className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/30 p-4 text-sm text-white/70">
      {label}
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
    </label>
  );
}

function NavButton({ icon: Icon, active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-left ${active ? "bg-white text-black" : "text-white/65 hover:bg-white/5"}`}
    >
      <Icon className="w-4 h-4" /> {children}
    </button>
  );
}

function App() {
  const [authMode, setAuthMode] = useState(null);
  const [initialEmail, setInitialEmail] = useState("");
  const [token, setToken] = useState(() => localStorage.getItem("asme_token") || "");
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!token) return;
    api("/api/auth/me", { token })
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("asme_token");
        setToken("");
      });
  }, [token]);

  function handleAuth(data) {
    localStorage.setItem("asme_token", data.token);
    setToken(data.token);
    setUser(data.user);
    setAuthMode(null);
  }

  function openAuth(mode, email = "") {
    setInitialEmail(email);
    setAuthMode(mode);
  }

  function logout() {
    localStorage.removeItem("asme_token");
    setToken("");
    setUser(null);
  }

  if (user) {
    return <Dashboard user={user} token={token} onLogout={logout} onUser={setUser} />;
  }

  return (
    <main className="relative bg-black h-screen w-screen flex flex-col overflow-hidden selection:bg-white selection:text-black shrink-0">
      <BackgroundVideo />
      <Navbar user={user} onOpenAuth={openAuth} onDashboard={() => openAuth("login")} onLogout={logout} />
      <Hero onOpenAuth={openAuth} />
      {authMode && (
        <AuthModal
          mode={authMode}
          initialEmail={initialEmail}
          onClose={() => setAuthMode(null)}
          onAuth={handleAuth}
        />
      )}
    </main>
  );
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (options.token) headers.Authorization = `Bearer ${options.token}`;
  const response = await fetch(path, { ...options, headers });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function fromCsv(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function toCsv(value) {
  return Array.isArray(value) ? value.join(", ") : "";
}

createRoot(document.getElementById("root")).render(<App />);
