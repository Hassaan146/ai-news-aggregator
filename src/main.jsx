import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { motion } from "motion/react";
import Hls from "hls.js";
import {
  CreditCard,
  Layers,
  Lock,
  LogOut,
  Mail,
  Newspaper,
  Shield,
  Settings,
  Sparkles,
  Star,
  User,
} from "lucide-react";
import "./index.css";

const VIDEO_URL =
  "https://stream.mux.com/kimF2ha9zLrX64H00UgLGPflCzNtl1T0215MlAmeOztv8.m3u8";

const defaultPrefs = {
  hours: 72,
  top_n: 10,
  profile_name: "default_ai_reader",
  use_llm: true,
  generate_missing_digests: true,
  preferred_sources: ["OpenAI News", "Anthropic News", "TechCrunch AI"],
  preferred_kinds: ["article", "youtube_video"],
  keywords: ["openai", "anthropic", "agents", "llm"],
  excluded_keywords: [],
};

const validationLimits = {
  minHours: 1,
  maxHours: 72,
  minTopDigests: 1,
  maxTopDigests: 10,
  maxSources: 20,
  maxKeywords: 20,
  maxKeywordLength: 40,
  maxReviewLength: 2000,
};

const IDLE_LOGOUT_MS = 5 * 60 * 1000;
const LAST_ACTIVITY_KEY = "asme_last_active";

const profileOptions = [
  {
    id: "default_ai_reader",
    title: "Balanced AI reader",
    text: "OpenAI, Anthropic, DeepMind, agents, research, and major product updates.",
  },
  {
    id: "openai_anthropic",
    title: "OpenAI + Anthropic",
    text: "Focused tracking for ChatGPT, Claude, model launches, and safety updates.",
  },
  {
    id: "builders",
    title: "Builder mode",
    text: "Developer tools, APIs, agents, RAG, open source, and implementation ideas.",
  },
];

const sourceOptions = [
  "OpenAI News",
  "OpenAI Blog",
  "Anthropic News",
  "Google DeepMind News",
  "Google AI Developers Blog",
  "Google Cloud Generative AI",
  "Hugging Face Blog",
  "Microsoft AI Blog",
  "Microsoft Semantic Kernel Blog",
  "GitHub Copilot Blog",
  "NVIDIA Generative AI",
  "IBM AI Blog",
  "Meta AI Blog",
  "Mistral AI News",
  "xAI News",
  "Cohere Blog",
  "Perplexity Blog",
  "TechCrunch AI",
  "The Verge AI",
  "VentureBeat AI",
  "MIT Technology Review AI",
  "WIRED AI",
  "Ars Technica AI",
  "The Decoder",
  "Unite.AI",
  "InfoQ AI ML Data Engineering",
  "MarkTechPost",
  "Latent Space",
  "The Sequence",
  "Interconnects",
  "The Batch",
  "LangChain Blog",
  "LlamaIndex Blog",
  "Weights & Biases Blog",
  "Pinecone Blog",
  "Weaviate Blog",
  "Qdrant Blog",
  "Together AI Blog",
  "Groq Blog",
  "AssemblyAI Blog",
  "Deepgram Blog",
  "Cursor Blog",
  "Vercel AI Blog",
  "Reuters AI",
  "AP Technology AI",
  "ZDNET AI",
  "The Register AI",
  "IEEE Spectrum AI",
  "Epoch AI Blog",
  "Stanford CRFM Blog",
  "MIT News AI",
  "CMU Machine Learning Blog",
  "Dark Reading AI",
  "Google Security AI",
  "Microsoft Security AI",
  "Lakera Blog",
  "Mozilla AI",
  "AI Incident Database Blog",
];

const keywordOptions = [
  "openai",
  "anthropic",
  "agents",
  "llm",
  "rag",
  "api",
  "research",
  "safety",
  "multimodal",
  "open source",
];

const contentTypeOptions = [
  ["article", "Articles"],
  ["youtube_video", "YouTube"],
];

function BrandMark({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <div className="grid h-10 w-10 place-items-center rounded-2xl border border-white/20 bg-white text-[#07111f] shadow-lg shadow-black/20">
        <div className="text-center leading-none">
          <div className="text-sm font-semibold tracking-[-0.02em]">AN</div>
          <div className="text-[8px] font-semibold uppercase tracking-[0.12em]">
            News
          </div>
        </div>
      </div>
      {!compact && (
        <div className="leading-tight text-left">
          <div className="text-sm font-semibold text-white">AI News</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-white/45">
            Aggregator
          </div>
        </div>
      )}
    </div>
  );
}

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
      <div className="absolute inset-0 bg-gradient-to-b from-[#0d1b32]/45 via-[#0b1020]/58 to-[#050914]/72" />
    </div>
  );
}

function Navbar({ user, onOpenAuth, onDashboard, onOpenInfo }) {
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
            <BrandMark />
          </button>
          <div className="hidden md:flex items-center gap-8 text-white/80 text-sm font-medium">
            {["Features", "Pricing", "About"].map((link) => (
              <button
                className="hover:text-white transition-colors duration-300"
                key={link}
                onClick={() => onOpenInfo(link.toLowerCase())}
                type="button"
              >
                {link}
              </button>
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
                Open app
              </button>
              <div className="liquid-glass rounded-full px-5 py-2 text-sm font-medium text-white/90">
                Active session
              </div>
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
            PERSONALIZED AI NEWS DIGESTS
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            style={{
              fontFamily: "'Instrument Serif', serif",
              textShadow: "0 18px 50px rgba(0,0,0,0.55), 0 2px 16px rgba(56,189,248,0.18)",
            }}
            className="text-4xl md:text-[64px] font-medium tracking-[-0.01em] leading-[1.1] mb-6 text-white max-w-4xl"
          >
            Daily AI news ranked around
            <br className="hidden md:block" /> what you care about
          </motion.h1>
          <p className="mx-auto max-w-2xl text-white/70 text-sm md:text-base leading-7">
            Track OpenAI, Anthropic, research labs, product launches, and trusted
            AI media in one personalized dashboard with daily email digests.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="min-h-[50px] mt-2"
        >
          <div className="flex flex-wrap items-center justify-center gap-3">
            <button
              className="rounded-full bg-white px-7 py-3 text-sm font-semibold text-[#07111f] transition-opacity hover:opacity-90"
              type="button"
              onClick={() => onOpenAuth("register")}
            >
              Create account
            </button>
            <button
              className="rounded-full border border-white/15 bg-white/[0.04] px-7 py-3 text-sm font-semibold text-white/85 transition-colors hover:border-white/35 hover:text-white"
              type="button"
              onClick={() => onOpenAuth("login")}
            >
              Login
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function InfoModal({ type, onClose, onOpenAuth }) {
  const content = {
    features: {
      eyebrow: "Features",
      title: "A personal operating layer for AI news",
      body: "AI News Aggregator combines source scraping, AI summarization, preference ranking, subscriptions, and email delivery into one workflow for tracking fast-moving AI updates.",
      items: [
        ["Priorities dashboard", "Pick profiles, sources, keywords, and content types with simple controls instead of raw setup."],
        ["Digest maker", "Choose top-N articles from any time window and rank them with LLM-based ranking plus deterministic fallback."],
        ["Subscription email agent", "Subscribed users get a daily 24-hour digest using the same saved preferences and ranking surface."],
      ],
    },
    pricing: {
      eyebrow: "Pricing",
      title: "Test the full payment path before charging users",
      body: "The current Stripe setup can save a card at $0.00 using Checkout setup mode. Later, you can switch to a live recurring Stripe Price for paid subscriptions.",
      items: [
        ["Free trial", "Use the dashboard, set priorities, and generate ranked digests."],
        ["Subscription flow", "Use Stripe Checkout to collect payment credentials safely and store subscription records."],
        ["Paid launch", "Set STRIPE_PRICE_ID to a live recurring price when you are ready to charge $1, $2, or more."],
      ],
    },
    about: {
      eyebrow: "About",
      title: "Built as an end-to-end AI news product",
      body: "The project is a deployable learning product: scrapers feed a database, digest agents summarize, ranking agents personalize, and the website exposes the workflow to users.",
      items: [
        ["Backend", "FastAPI, PostgreSQL, SQLAlchemy, Gemini-powered digest and ranking agents."],
        ["Frontend", "React, Vite, Tailwind CSS v4, Motion, Lucide icons, HLS background video."],
        ["Payments", "Stripe Checkout with local records for users, subscriptions, and transactions."],
      ],
    },
  }[type];

  if (!content) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="liquid-glass w-full max-w-3xl rounded-[30px] p-7"
      >
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-white/50 text-xs uppercase tracking-[0.2em]">
              {content.eyebrow}
            </p>
            <h2
              style={{ fontFamily: "'Instrument Serif', serif" }}
              className="mt-2 text-4xl md:text-5xl leading-tight"
            >
              {content.title}
            </h2>
            <p className="mt-4 text-white/65 leading-7 max-w-2xl">
              {content.body}
            </p>
          </div>
          <button className="text-white/60" onClick={onClose} type="button">
            Close
          </button>
        </div>
        <div className="mt-7 grid md:grid-cols-3 gap-3">
          {content.items.map(([title, text]) => (
            <div
              key={title}
              className="rounded-3xl border border-white/10 bg-white/[0.035] p-4"
            >
              <h3 className="font-semibold">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-white/55">{text}</p>
            </div>
          ))}
        </div>
        <button
          className="mt-7 rounded-full bg-white px-5 py-3 font-semibold text-[#07111f]"
          onClick={() => onOpenAuth("register")}
          type="button"
        >
          Create account
        </button>
      </motion.div>
    </div>
  );
}

function AuthModal({ mode, initialEmail, onClose, onAuth }) {
  const [isRegister, setIsRegister] = useState(mode !== "login");
  const [form, setForm] = useState({
    name: "",
    email: initialEmail || "",
    password: "",
  });
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => setIsRegister(mode !== "login"), [mode]);

  async function submit(event) {
    event.preventDefault();
    if (isSubmitting) return;
    setError("");
    setNotice("");
    const email = form.email.trim();
    const password = form.password.trim();
    const name = form.name.trim();
    if (isRegister && !name) {
      setError("Please enter your name.");
      return;
    }
    if (name.length > 80) {
      setError("Name must be 80 characters or fewer.");
      return;
    }
    if (!email) {
      setError("Please enter your email.");
      return;
    }
    if (!isValidEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (password.length > 128) {
      setError("Password must be 128 characters or fewer.");
      return;
    }

    setIsSubmitting(true);
    setNotice(isRegister ? "Creating your account..." : "Logging you in...");
    try {
      const data = await api(`/api/auth/${isRegister ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify({ ...form, name, email, password }),
      });
      if (isRegister) {
        setNotice("Account created. Please login with the same email and password.");
        setIsRegister(false);
        setForm({ ...form, password: "" });
        return;
      }
      onAuth(data);
    } catch (err) {
      setNotice("");
      setError(err.message);
    } finally {
      setIsSubmitting(false);
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
        {notice && <p className="mb-4 rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-3 text-sm text-emerald-100">{notice}</p>}
        <div className="grid gap-4">
          {isRegister && (
            <Field
              icon={User}
              label="Name"
              value={form.name}
              maxLength={80}
              onChange={(name) => setForm({ ...form, name })}
            />
          )}
          <Field
            icon={Mail}
            label="Email"
            value={form.email}
            type="email"
            maxLength={254}
            onChange={(email) => setForm({ ...form, email })}
          />
          <Field
            icon={Lock}
            label="Password"
            value={form.password}
            type="password"
            maxLength={128}
            onChange={(password) => setForm({ ...form, password })}
          />
        </div>
        {error && (
          <pre className="mt-4 max-h-44 overflow-auto whitespace-pre-wrap rounded-2xl border border-red-300/20 bg-red-950/30 p-3 text-xs leading-5 text-red-100">
            {error}
          </pre>
        )}
        <button
          className={`mt-6 w-full rounded-full bg-white text-black py-3 font-semibold transition-opacity ${isSubmitting ? "cursor-wait opacity-70" : "hover:opacity-90"}`}
          disabled={isSubmitting}
          type="submit"
        >
          {isSubmitting
            ? isRegister
              ? "Creating account..."
              : "Logging in..."
            : isRegister
              ? "Register"
              : "Login"}
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
  const [prefs, setPrefs] = useState(() => normalizePreferences(user.preferences));
  const [digests, setDigests] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [adminData, setAdminData] = useState(null);
  const [message, setMessage] = useState("");
  const [isDigestLoading, setIsDigestLoading] = useState(false);
  const [showGuide, setShowGuide] = useState(() => {
    return localStorage.getItem(`asme_guide_seen_${user.id}`) !== "1";
  });

  function closeGuide() {
    localStorage.setItem(`asme_guide_seen_${user.id}`, "1");
    setShowGuide(false);
  }

  async function savePrefs() {
    const validationError = validateDigestPreferences(prefs);
    if (validationError) {
      setMessage(validationError);
      return;
    }
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
    const validationError = validateDigestPreferences(prefs);
    if (validationError) {
      setMessage(validationError);
      return;
    }
    setIsDigestLoading(true);
    setMessage("Creating your digest. The app will map your priorities, fetch matching sources into the database, generate AI digest rows, then rank them. Please wait around 90-120 seconds.");
    try {
      const data = await api("/api/dashboard/digests", {
        method: "POST",
        token,
        body: JSON.stringify(prefs),
      });
      setDigests(data);
      setPage("digests");
      const generation = data.digest_generation;
      const scrape = data.scrape_result;
      const generationText = generation
        ? ` Digests processed: ${generation.processed}, saved: ${generation.created_or_updated}${generation.stopped_reason ? `, stopped: ${generation.stopped_reason}` : ""}.`
        : "";
      const scrapeText = scrape
        ? ` Sources checked/stored: ${scrape.stored_or_updated}.`
        : "";
      const llmText = data.llm_status?.message ? ` ${data.llm_status.message}` : "";
      const emptyText = data.total_items === 0
        ? " No digest rows were available after scraping and generation. Try a larger time window, then check backend logs if this keeps happening."
        : "";
      setMessage(`${data.ranking_method.toUpperCase()} ranking returned ${data.total_items} items.${scrapeText}${generationText}${llmText}${emptyText}`);
    } catch (err) {
      setMessage(err.message);
    } finally {
      setIsDigestLoading(false);
    }
  }

  async function startCheckout() {
    const accountError = validateAccountIdentity(user);
    if (accountError) {
      setMessage(accountError);
      return;
    }
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

  async function loadReviews() {
    setMessage("Loading reviews...");
    try {
      const data = await api("/api/reviews", { token });
      setReviews(data);
      setPage("reviews");
      setMessage("");
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function saveReview(payload) {
    const validationError = validateReviewPayload(payload);
    if (validationError) {
      setMessage(validationError);
      return;
    }
    setMessage("Saving your review...");
    try {
      const data = await api("/api/reviews", {
        method: "POST",
        token,
        body: JSON.stringify(payload),
      });
      setReviews((current) => ({
        my_review: data.review,
        reviews: [
          data.review,
          ...((current?.reviews || []).filter((review) => review.id !== data.review.id)),
        ].slice(0, 12),
      }));
      setMessage("Thanks. Your review was saved.");
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function loadAdmin() {
    setMessage("Loading admin dashboard...");
    try {
      const data = await api("/api/admin/overview", { token });
      setAdminData(data);
      setPage("admin");
      setMessage("");
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <main className="relative min-h-screen dashboard-atmosphere text-white overflow-hidden">
      <BackgroundVideo />
      <div className="absolute inset-0 bg-[#07111f]/58" />
      <div className="relative z-10 min-h-screen dashboard-grid p-4 gap-4">
        <aside className="liquid-glass rounded-[32px] p-5">
          <div className="mb-8">
            <BrandMark />
          </div>
          <nav className="grid gap-2">
            <NavButton icon={Settings} active={page === "preferences"} onClick={() => setPage("preferences")}>Priorities</NavButton>
            <NavButton icon={Newspaper} active={page === "digests"} onClick={() => setPage("digests")}>Digest maker</NavButton>
            <NavButton icon={CreditCard} active={page === "subscription"} onClick={() => setPage("subscription")}>Subscription</NavButton>
            <NavButton icon={Star} active={page === "reviews"} onClick={loadReviews}>Reviews</NavButton>
            {user.is_admin && (
              <NavButton icon={Shield} active={page === "admin"} onClick={loadAdmin}>Admin</NavButton>
            )}
          </nav>
          <button
            type="button"
            className="mt-8 flex items-center gap-2 text-white/55 hover:text-white"
            onClick={onLogout}
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </aside>
        <section className="overflow-auto rounded-[32px] border border-white/15 bg-[#0f1a2d]/55 backdrop-blur-xl p-5 md:p-8 shadow-2xl shadow-black/20">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div>
              <p className="text-white/50 text-sm">Workspace</p>
              <h1 className="text-3xl md:text-5xl font-semibold tracking-[-0.03em]">AI news dashboard</h1>
            </div>
            <div className="glass-pill px-4 py-2 text-sm text-white/80">
              {user.name} · {user.subscription_status || "free"} plan
            </div>
          </div>
        {message && <div className="mb-5 rounded-2xl bg-white/10 border border-white/15 p-4 text-sm text-white/85">{message}</div>}
          {page === "preferences" && (
            <Preferences prefs={prefs} setPrefs={setPrefs} onSave={savePrefs} onRun={loadDigests} onInvalid={setMessage} isDigestLoading={isDigestLoading} />
          )}
          {page === "digests" && (
            <DigestMaker prefs={prefs} setPrefs={setPrefs} onRun={loadDigests} digests={digests} isDigestLoading={isDigestLoading} />
          )}
          {page === "subscription" && (
            <Subscription user={user} onCheckout={startCheckout} />
          )}
          {page === "reviews" && (
            <ReviewsPanel reviews={reviews} onSave={saveReview} />
          )}
          {page === "admin" && user.is_admin && (
            <AdminPanel data={adminData} onRefresh={loadAdmin} />
          )}
        </section>
      </div>
      {showGuide && (
        <GuideModal
          onClose={closeGuide}
          onStart={() => {
            setPage("preferences");
            closeGuide();
          }}
        />
      )}
    </main>
  );
}

function GuideModal({ onClose, onStart }) {
  const steps = [
    {
      title: "Choose priorities",
      text: "Start with a preset, then select the sources and topics you care about. This tells the ranking system what to prefer.",
    },
    {
      title: "Generate a digest",
      text: "Open Digest maker, choose how many hours and how many articles you want, then generate your ranked news list.",
    },
    {
      title: "Subscribe for emails",
      text: "Use the Subscription page to connect Stripe Checkout. Subscribed users can receive the daily 24-hour email digest.",
    },
  ];

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="liquid-glass w-full max-w-4xl rounded-[32px] p-7"
      >
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-white/50 text-xs uppercase tracking-[0.2em]">
              Quick guide
            </p>
            <h2
              style={{ fontFamily: "'Instrument Serif', serif" }}
              className="mt-2 text-4xl md:text-5xl leading-tight"
            >
              Here is how to use AI News
            </h2>
            <p className="mt-4 max-w-2xl text-white/65 leading-7">
              The app has three simple areas: priorities, digest making, and
              subscription. Follow these once and the workflow becomes natural.
            </p>
          </div>
          <button className="text-white/60 hover:text-white" onClick={onClose} type="button">
            Skip
          </button>
        </div>

        <div className="mt-7 grid md:grid-cols-3 gap-3">
          {steps.map((step, index) => (
            <div
              key={step.title}
              className="rounded-3xl border border-white/15 bg-white/[0.07] p-5"
            >
              <div className="mb-4 grid h-10 w-10 place-items-center rounded-full bg-white text-black font-semibold">
                {index + 1}
              </div>
              <h3 className="font-semibold text-lg">{step.title}</h3>
              <p className="mt-2 text-sm leading-6 text-white/60">{step.text}</p>
            </div>
          ))}
        </div>

        <div className="mt-7 flex flex-wrap gap-3">
          <button
            className="rounded-full bg-white px-6 py-3 font-semibold text-black"
            onClick={onStart}
            type="button"
          >
            Start with priorities
          </button>
          <button
            className="rounded-full border border-white/15 px-6 py-3 font-semibold text-white/80"
            onClick={onClose}
            type="button"
          >
            I know what to do
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function Preferences({ prefs, setPrefs, onSave, onRun, onInvalid, isDigestLoading }) {
  const [customKeyword, setCustomKeyword] = useState("");

  function applyProfile(profileName) {
    const profileDefaults = {
      default_ai_reader: {
        preferred_sources: ["OpenAI News", "OpenAI Blog", "Anthropic News", "Google DeepMind News", "Hugging Face Blog", "TechCrunch AI"],
        preferred_kinds: ["article", "youtube_video"],
        keywords: ["openai", "anthropic", "agents", "llm", "research", "safety"],
      },
      openai_anthropic: {
        preferred_sources: ["OpenAI News", "OpenAI Blog", "Anthropic News"],
        preferred_kinds: ["article"],
        keywords: ["openai", "anthropic", "claude", "chatgpt", "model", "agent"],
      },
      builders: {
        preferred_sources: ["Hugging Face Blog", "TechCrunch AI"],
        preferred_kinds: ["article", "youtube_video"],
        keywords: ["python", "agent", "rag", "api", "developer", "open source"],
      },
    }[profileName];
    setPrefs({ ...prefs, profile_name: profileName, ...profileDefaults });
  }

  function addCustomKeyword() {
    const value = customKeyword.trim().toLowerCase();
    if (!value) return;
    if (!isSafeShortText(value)) {
      onInvalid("Custom topics can use letters, numbers, spaces, hyphens, dots, apostrophes, slashes, plus signs, and # only.");
      return;
    }
    if (value.length > validationLimits.maxKeywordLength) {
      onInvalid(`Custom topics must be ${validationLimits.maxKeywordLength} characters or fewer.`);
      return;
    }
    const existingKeywords = prefs.keywords || [];
    if (!existingKeywords.includes(value) && existingKeywords.length >= validationLimits.maxKeywords) {
      onInvalid(`You can add up to ${validationLimits.maxKeywords} topics. Remove one before adding another.`);
      return;
    }
    setPrefs({ ...prefs, keywords: Array.from(new Set([...existingKeywords, value])) });
    setCustomKeyword("");
  }

  return (
    <Panel title="Choose what you care about" description="Start from a preset, then tap sources and topics to fine tune the feed.">
      <div className="grid md:grid-cols-3 gap-3">
        {profileOptions.map((profile) => (
          <button
            key={profile.id}
            type="button"
            onClick={() => applyProfile(profile.id)}
          className={`rounded-3xl border p-4 text-left transition-all ${prefs.profile_name === profile.id ? "border-white/55 bg-white/18" : "border-white/15 bg-white/[0.07] hover:bg-white/[0.11]"}`}
          >
            <h3 className="font-semibold">{profile.title}</h3>
            <p className="mt-2 text-sm leading-6 text-white/55">{profile.text}</p>
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <PreferenceTable
          title="Source feeds"
          eyebrow="Where news comes from"
          description="Official blogs, AI labs, media sites, and trusted update channels."
          tone="cyan"
          values={prefs.preferred_sources || []}
          options={sourceOptions}
          maxSelected={validationLimits.maxSources}
          onChange={(preferred_sources) => setPrefs({ ...prefs, preferred_sources })}
        />

        <div className="rounded-3xl border border-violet-300/20 bg-violet-300/[0.055] p-4">
          <PreferenceTable
            title="Topic keywords"
            eyebrow="What the ranking prefers"
            description="Signals used to prioritize the articles and videos most relevant to you."
            tone="violet"
            values={prefs.keywords || []}
            options={keywordOptions}
            maxSelected={validationLimits.maxKeywords}
            onChange={(keywords) => setPrefs({ ...prefs, keywords })}
            embedded
          />
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3">
            <label className="text-xs font-medium uppercase tracking-[0.16em] text-violet-100/70">
              Add custom topic
            </label>
            <div className="mt-2 flex gap-2">
              <input
                className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
                value={customKeyword}
                onChange={(event) => setCustomKeyword(event.target.value)}
                placeholder="robotics, evals, startups"
              />
              <button className="rounded-2xl bg-violet-200 px-4 text-sm font-semibold text-[#160f2d]" type="button" onClick={addCustomKeyword}>Add</button>
            </div>
          </div>
        </div>

        <PreferenceTable
          title="Content types"
          eyebrow="Format filters"
          description="Choose whether the digest should include written posts, YouTube updates, or both."
          tone="emerald"
          values={prefs.preferred_kinds || []}
          options={contentTypeOptions.map(([id]) => id)}
          labels={Object.fromEntries(contentTypeOptions)}
          onChange={(preferred_kinds) => setPrefs({ ...prefs, preferred_kinds })}
        />
      </div>

      <div className="mt-5 rounded-3xl border border-white/15 bg-white/[0.06] p-4">
        <Toggle label="Use LLM ranking when available" checked={prefs.use_llm} onChange={(use_llm) => setPrefs({ ...prefs, use_llm })} />
      </div>
      <div className="flex gap-3 mt-6">
        <button className="rounded-full bg-white text-black px-5 py-3 font-semibold" onClick={onSave} type="button">Save priorities</button>
        <button
          className={`rounded-full border border-white/15 px-5 py-3 font-semibold ${isDigestLoading ? "cursor-wait opacity-60" : ""}`}
          disabled={isDigestLoading}
          onClick={onRun}
          type="button"
        >
          {isDigestLoading ? "Generating..." : "Generate digest"}
        </button>
      </div>
    </Panel>
  );
}

function PreferenceTable({
  title,
  eyebrow,
  description,
  tone,
  options,
  values,
  onChange,
  maxSelected,
  labels = {},
  embedded = false,
}) {
  const tones = {
    cyan: {
      shell: "border-cyan-300/20 bg-cyan-300/[0.055]",
      badge: "bg-cyan-200 text-[#06242b]",
      selected: "border-cyan-200/70 bg-cyan-200 text-[#06242b]",
      accent: "text-cyan-100/70",
    },
    violet: {
      shell: "border-transparent bg-transparent p-0",
      badge: "bg-violet-200 text-[#160f2d]",
      selected: "border-violet-200/70 bg-violet-200 text-[#160f2d]",
      accent: "text-violet-100/70",
    },
    emerald: {
      shell: "border-emerald-300/20 bg-emerald-300/[0.055]",
      badge: "bg-emerald-200 text-[#062b1e]",
      selected: "border-emerald-200/70 bg-emerald-200 text-[#062b1e]",
      accent: "text-emerald-100/70",
    },
  }[tone];

  function toggle(option) {
    if (!values.includes(option) && maxSelected && values.length >= maxSelected) {
      return;
    }
    const next = values.includes(option)
      ? values.filter((item) => item !== option)
      : [...values, option];
    onChange(next);
  }

  return (
    <section className={embedded ? "" : `rounded-3xl border p-4 ${tones.shell}`}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className={`text-[10px] font-semibold uppercase tracking-[0.18em] ${tones.accent}`}>
            {eyebrow}
          </p>
          <h3 className="mt-1 text-lg font-semibold text-white">{title}</h3>
          <p className="mt-2 text-sm leading-6 text-white/55">{description}</p>
        </div>
        <div className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${tones.badge}`}>
          {values.length}/{maxSelected || options.length}
        </div>
      </div>

      <div className="grid gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => toggle(option)}
            className={`flex items-center justify-between gap-3 rounded-2xl border px-3 py-3 text-left text-sm transition-colors ${
              values.includes(option)
                ? tones.selected
                : maxSelected && values.length >= maxSelected
                  ? "cursor-not-allowed border-white/10 bg-black/10 text-white/30"
                  : "border-white/10 bg-black/20 text-white/72 hover:border-white/25 hover:text-white"
            }`}
          >
            <span className="font-medium">{labels[option] || option}</span>
            <span className="grid h-5 w-5 place-items-center rounded-full border border-current text-[10px]">
              {values.includes(option) ? "✓" : "+"}
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}

function DigestMaker({ prefs, setPrefs, onRun, digests, isDigestLoading }) {
  return (
    <div className="grid gap-5">
      <Panel title="Digest making" description="Generate missing digest rows, save them to the database, then rank the saved digests for this user.">
        <div className="grid md:grid-cols-3 gap-4">
          <Field
            label="Last hours"
            type="number"
            min={validationLimits.minHours}
            max={validationLimits.maxHours}
            value={prefs.hours}
            onChange={(hours) => setPrefs({ ...prefs, hours: Number(hours) })}
          />
          <Field
            label="Top digests"
            type="number"
            min={validationLimits.minTopDigests}
            max={validationLimits.maxTopDigests}
            value={prefs.top_n}
            onChange={(top_n) => setPrefs({ ...prefs, top_n: Number(top_n) })}
          />
          <Toggle label="Use LLM ranking" checked={prefs.use_llm} onChange={(use_llm) => setPrefs({ ...prefs, use_llm })} />
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-[minmax(0,1fr)_320px]">
          <div className="rounded-3xl border border-white/15 bg-white/[0.06] p-4 text-sm leading-6 text-white/65">
            Digest and ranking agents use the secure backend AI key configured in Render.
          </div>
          <Toggle
            label="Create missing digests first"
            checked={prefs.generate_missing_digests !== false}
            onChange={(generate_missing_digests) => setPrefs({ ...prefs, generate_missing_digests })}
          />
        </div>
        <p className="mt-3 text-sm leading-6 text-white/55">
          If the LLM fails or hits a limit, the backend saves deterministic fallback digests
          so the dashboard can still show items.
        </p>
        <button
          className={`mt-5 rounded-full bg-white text-black px-5 py-3 font-semibold ${isDigestLoading ? "cursor-wait opacity-60" : ""}`}
          disabled={isDigestLoading}
          onClick={onRun}
          type="button"
        >
          {isDigestLoading ? "Working for up to 2 minutes..." : "Make and rank digests"}
        </button>
      </Panel>
      {digests && (
        <section className="liquid-glass rounded-[30px] p-5">
          <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/45">
                Personalized digest
              </p>
              <h2 className="mt-1 text-2xl font-semibold">Top {digests.total_items} AI updates</h2>
              <p className="mt-2 text-sm leading-6 text-white/55">
                Ranked with {digests.ranking_method} logic across the last {digests.lookback_hours} hours.
                {digests.digest_generation
                  ? ` Generated ${digests.digest_generation.created_or_updated} new digest rows from ${digests.digest_generation.processed} stored articles.`
                  : ""}
              </p>
            </div>
            <div className="rounded-full border border-white/10 bg-white/[0.06] px-4 py-2 text-sm text-white/70">
              Max 10 articles
            </div>
          </div>
          <div className="grid gap-4">
          {digests.items.map((item) => (
            <article className="rounded-[28px] border border-white/10 bg-[#111f36]/80 p-5 shadow-xl shadow-black/10" key={item.identity_key}>
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="grid h-8 w-8 place-items-center rounded-full bg-white text-sm font-semibold text-[#07111f]">
                  {item.rank}
                </span>
                <span className="rounded-full border border-cyan-200/20 bg-cyan-200/10 px-3 py-1 font-medium text-cyan-100">
                  {item.source}
                </span>
                <span className="rounded-full border border-emerald-200/20 bg-emerald-200/10 px-3 py-1 font-medium text-emerald-100">
                  {item.kind.replace("_", " ")}
                </span>
                <span className="rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-white/60">
                  {formatDigestDate(item.published_at)}
                </span>
                <span className="ml-auto rounded-full border border-white/10 bg-black/20 px-3 py-1 text-white/55">
                  score {item.score}
                </span>
              </div>
              <h3 className="mt-4 text-xl font-semibold leading-snug text-white">
                {item.title}
              </h3>
              <p className="mt-3 rounded-3xl border border-white/10 bg-black/20 p-4 text-[15px] leading-8 text-white/80">
                {item.summary}
              </p>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap gap-2">
                  {(item.matched_reasons || []).slice(0, 4).map((reason) => (
                    <span key={reason} className="rounded-full bg-white/[0.07] px-3 py-1 text-xs text-white/50">
                      {formatReason(reason)}
                    </span>
                  ))}
                </div>
                <a
                  className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-[#07111f] transition-opacity hover:opacity-90"
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Read original
                </a>
              </div>
            </article>
          ))}
          </div>
          {!digests.items.length && (
            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 text-white/60">
              No readable digest rows were available yet. Generate again after the scraper has saved fresh source items.
            </div>
          )}
        </section>
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
        <div className="mt-5 grid gap-2 text-sm text-white/60">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4" /> Plan: AI News Daily Email
          </div>
          <div className="flex items-center gap-2">
            <CreditCard className="w-4 h-4" /> Current setup: $0.00 card setup
          </div>
        </div>
        <div className="mt-5 text-sm text-white/60">Account: {user.email}</div>
        <button className="mt-6 rounded-full bg-white text-black px-6 py-3 font-semibold" onClick={onCheckout} type="button">Try payment</button>
      </div>
    </Panel>
  );
}

function ReviewsPanel({ reviews, onSave }) {
  const [rating, setRating] = useState(reviews?.my_review?.rating || 5);
  const [reviewText, setReviewText] = useState(reviews?.my_review?.review_text || "");

  useEffect(() => {
    setRating(reviews?.my_review?.rating || 5);
    setReviewText(reviews?.my_review?.review_text || "");
  }, [reviews]);

  return (
    <Panel
      title="Reviews"
      description="Tell us how the AI News Aggregator feels to use. Pick a star rating and add a custom review."
    >
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="rounded-3xl border border-white/15 bg-white/[0.06] p-5">
          <p className="mb-3 text-sm font-medium text-white/70">Your rating</p>
          <div className="flex flex-wrap gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                className={`grid h-12 w-12 place-items-center rounded-2xl border transition-colors ${
                  star <= rating
                    ? "border-yellow-300/70 bg-yellow-300 text-[#07111f]"
                    : "border-white/15 bg-white/[0.05] text-white/45 hover:text-white"
                }`}
                aria-label={`${star} star${star === 1 ? "" : "s"}`}
              >
                <Star className="h-5 w-5" fill={star <= rating ? "currentColor" : "none"} />
              </button>
            ))}
          </div>
          <label className="mt-5 grid gap-2 text-sm text-white/65">
            Custom review
            <textarea
              className="min-h-[160px] rounded-3xl border border-white/15 bg-[#101b2e] p-4 text-white outline-none placeholder:text-white/35"
              value={reviewText}
              onChange={(event) => setReviewText(event.target.value)}
              placeholder="What worked well? What should improve?"
              maxLength={2000}
            />
          </label>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button
              className="rounded-full bg-white px-6 py-3 font-semibold text-[#07111f]"
              onClick={() => onSave({ rating, review_text: reviewText })}
              type="button"
            >
              Save review
            </button>
            <span className="text-sm text-white/45">{reviewText.length}/2000</span>
          </div>
        </div>

        <div className="rounded-3xl border border-white/15 bg-white/[0.06] p-5">
          <h3 className="font-semibold">Recent reviews</h3>
          <div className="mt-4 grid gap-3">
            {(reviews?.reviews || []).length ? (
              reviews.reviews.map((review) => (
                <div key={review.id} className="rounded-2xl border border-white/10 bg-white/[0.045] p-4">
                  <div className="mb-2 flex gap-1 text-yellow-300">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className="h-4 w-4"
                        fill={star <= review.rating ? "currentColor" : "none"}
                      />
                    ))}
                  </div>
                  <p className="text-sm leading-6 text-white/70">
                    {review.review_text || "No written review added."}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-sm leading-6 text-white/55">
                No reviews yet. Yours can be the first one.
              </p>
            )}
          </div>
        </div>
      </div>
    </Panel>
  );
}

function AdminPanel({ data, onRefresh }) {
  const summary = data?.summary || {};
  const stats = [
    ["Users", summary.users || 0],
    ["Reviews", summary.reviews || 0],
    ["Subscriptions", summary.subscriptions || 0],
    ["Active subs", summary.active_subscriptions || 0],
    ["Transactions", summary.transactions || 0],
    ["Revenue", formatMoney(summary.total_amount_cents || 0, "usd")],
    ["News items", summary.news_items || 0],
    ["Digest rows", summary.digest_items || 0],
  ];

  return (
    <Panel
      title="Admin view"
      description="Monitor users, reviews, payments, subscriptions, and database activity."
    >
      <div className="mb-5 flex justify-end">
        <button
          className="rounded-full bg-white px-5 py-2 text-sm font-semibold text-[#07111f]"
          onClick={onRefresh}
          type="button"
        >
          Refresh
        </button>
      </div>

      {!data ? (
        <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-5 text-white/60">
          Click refresh to load the admin data.
        </div>
      ) : (
        <div className="grid gap-5">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {stats.map(([label, value]) => (
              <div key={label} className="rounded-3xl border border-white/10 bg-white/[0.06] p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-white/40">{label}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
              </div>
            ))}
          </div>

          <AdminTable
            title="Recent users"
            rows={data.users || []}
            columns={[
              ["name", "Name"],
              ["email", "Email"],
              ["subscription_status", "Plan status"],
              ["created_at", "Created"],
            ]}
          />
          <AdminTable
            title="Reviews"
            rows={data.reviews || []}
            columns={[
              ["user_name", "User"],
              ["user_email", "Email"],
              ["rating", "Rating"],
              ["review_text", "Review"],
              ["updated_at", "Updated"],
            ]}
          />
          <AdminTable
            title="Subscriptions"
            rows={data.subscriptions || []}
            columns={[
              ["user_email", "Email"],
              ["plan_name", "Plan"],
              ["status", "Status"],
              ["mode", "Mode"],
              ["amount_cents", "Amount"],
              ["created_at", "Created"],
            ]}
            formatValue={(key, value, row) =>
              key === "amount_cents" ? formatMoney(value, row.currency) : value
            }
          />
          <AdminTable
            title="Transactions"
            rows={data.transactions || []}
            columns={[
              ["user_email", "Email"],
              ["status", "Status"],
              ["amount_cents", "Amount"],
              ["stripe_checkout_session_id", "Checkout session"],
              ["created_at", "Created"],
            ]}
            formatValue={(key, value, row) =>
              key === "amount_cents" ? formatMoney(value, row.currency) : value
            }
          />
        </div>
      )}
    </Panel>
  );
}

function AdminTable({ title, rows, columns, formatValue }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="font-semibold text-white">{title}</h3>
        <span className="rounded-full bg-white/[0.08] px-3 py-1 text-xs text-white/50">
          {rows.length} rows
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="text-xs uppercase tracking-[0.14em] text-white/40">
            <tr>
              {columns.map(([, label]) => (
                <th className="border-b border-white/10 px-3 py-3 font-medium" key={label}>
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="text-white/70">
            {rows.length ? (
              rows.map((row) => (
                <tr key={`${title}-${row.id}`} className="border-b border-white/5">
                  {columns.map(([key]) => (
                    <td className="max-w-[280px] px-3 py-3 align-top" key={key}>
                      <span className="line-clamp-3">
                        {formatAdminValue(formatValue ? formatValue(key, row[key], row) : row[key])}
                      </span>
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-3 py-5 text-white/45" colSpan={columns.length}>
                  No records yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Panel({ title, description, children }) {
  return (
    <section className="liquid-glass rounded-[30px] p-6">
      <h2 className="text-2xl font-semibold">{title}</h2>
      <p className="mt-2 mb-6 text-white/55">{description}</p>
      {children}
    </section>
  );
}

function Field({ label, value, onChange, type = "text", icon: Icon, min, max, maxLength }) {
  return (
    <label className="grid gap-2 text-sm text-white/60">
      {label}
      <div className="flex items-center gap-2 rounded-2xl border border-white/15 bg-white/[0.07] px-3">
        {Icon && <Icon className="w-4 h-4 text-white/40" />}
        <input
          className="w-full bg-transparent py-3 outline-none text-white"
          type={type}
          min={min}
          max={max}
          maxLength={maxLength}
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
        className="min-h-[96px] rounded-2xl border border-white/15 bg-white/[0.07] p-3 outline-none text-white"
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
        className="rounded-2xl border border-white/15 bg-[#132039] p-3 outline-none text-white"
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
    <label className="flex items-center justify-between rounded-2xl border border-white/15 bg-white/[0.07] p-4 text-sm text-white/80">
      {label}
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
    </label>
  );
}

function validateDigestPreferences(prefs) {
  const hours = Number(prefs.hours);
  const topDigests = Number(prefs.top_n);
  const sources = prefs.preferred_sources || [];
  const kinds = prefs.preferred_kinds || [];
  const keywords = prefs.keywords || [];

  if (!Number.isInteger(hours) || hours < validationLimits.minHours || hours > validationLimits.maxHours) {
    return `Please choose a lookback window between ${validationLimits.minHours} and ${validationLimits.maxHours} hours.`;
  }
  if (!Number.isInteger(topDigests) || topDigests < validationLimits.minTopDigests || topDigests > validationLimits.maxTopDigests) {
    return `You can request between ${validationLimits.minTopDigests} and ${validationLimits.maxTopDigests} digests at once.`;
  }
  if (!sources.length) {
    return "Please select at least one source feed before generating a digest.";
  }
  if (sources.length > validationLimits.maxSources) {
    return `Please select no more than ${validationLimits.maxSources} source feeds.`;
  }
  if (!kinds.length) {
    return "Please select at least one content type.";
  }
  if (!keywords.length) {
    return "Please select or add at least one topic keyword.";
  }
  if (keywords.length > validationLimits.maxKeywords) {
    return `Please keep topic keywords to ${validationLimits.maxKeywords} or fewer.`;
  }
  if (keywords.some((keyword) => String(keyword).trim().length > validationLimits.maxKeywordLength)) {
    return `Each topic keyword must be ${validationLimits.maxKeywordLength} characters or fewer.`;
  }
  if ([...sources, ...keywords, ...(prefs.excluded_keywords || [])].some((value) => !isSafeShortText(value))) {
    return "Sources and keywords can only contain safe text characters. Remove symbols like <, >, quotes, semicolons, or backslashes.";
  }
  if (kinds.some((kind) => !["article", "youtube_video"].includes(kind))) {
    return "Please choose a valid content type.";
  }
  return "";
}

function normalizePreferences(preferences) {
  const merged = { ...defaultPrefs, ...(preferences || {}) };
  return {
    ...merged,
    hours: clampInteger(merged.hours, 72, validationLimits.minHours, validationLimits.maxHours),
    top_n: clampInteger(
      merged.top_n,
      10,
      validationLimits.minTopDigests,
      validationLimits.maxTopDigests,
    ),
  };
}

function clampInteger(value, fallback, min, max) {
  const number = Number(value);
  if (!Number.isInteger(number)) return fallback;
  return Math.min(Math.max(number, min), max);
}

function validateAccountIdentity(user) {
  if (!user?.name?.trim()) return "Your account name is missing. Please log out and register again.";
  if (!isValidEmail(user.email)) return "Your account email is invalid. Please use a valid email before checkout.";
  return "";
}

function validateReviewPayload(payload) {
  const rating = Number(payload.rating);
  const text = payload.review_text || "";
  if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
    return "Please choose a star rating between 1 and 5.";
  }
  if (text.length > validationLimits.maxReviewLength) {
    return `Your review must be ${validationLimits.maxReviewLength} characters or fewer.`;
  }
  return "";
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || "").trim());
}

function isSafeShortText(value) {
  return /^[\w\s.#/+&():,'-]+$/u.test(String(value || "").trim());
}

function formatDigestDate(value) {
  if (!value) return "latest undated";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "latest undated";
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatReason(reason) {
  return String(reason || "")
    .replace("source:", "source: ")
    .replace("keyword:", "topic: ")
    .replace("kind:", "type: ")
    .replace("ranked_by:", "ranked by ")
    .replaceAll("_", " ");
}

function formatAdminValue(value) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "string" && value.includes("T")) {
    const date = new Date(value);
    if (!Number.isNaN(date.getTime())) {
      return date.toLocaleString();
    }
  }
  return String(value);
}

function formatMoney(cents, currency = "usd") {
  const amount = Number(cents || 0) / 100;
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: String(currency || "usd").toUpperCase(),
  }).format(amount);
}

function formatBackendDetail(detail) {
  if (!detail) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        const location = Array.isArray(item.loc) ? item.loc.join(".") : item.loc;
        const message = item.msg || item.message || JSON.stringify(item);
        return location ? `${location}: ${message}` : message;
      })
      .join("\n");
  }
  return JSON.stringify(detail, null, 2);
}

function NavButton({ icon: Icon, active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-left ${active ? "bg-white text-black" : "text-white/75 hover:bg-white/10"}`}
    >
      <Icon className="w-4 h-4" /> {children}
    </button>
  );
}

function App() {
  const [authMode, setAuthMode] = useState(null);
  const [infoModal, setInfoModal] = useState(null);
  const [initialEmail, setInitialEmail] = useState("");
  const [token, setToken] = useState(() => {
    const storedToken = localStorage.getItem("asme_token") || "";
    const lastActive = Number(localStorage.getItem(LAST_ACTIVITY_KEY) || Date.now());
    if (storedToken && Date.now() - lastActive > IDLE_LOGOUT_MS) {
      localStorage.removeItem("asme_token");
      localStorage.removeItem("asme_user");
      localStorage.removeItem(LAST_ACTIVITY_KEY);
      return "";
    }
    return storedToken;
  });
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("asme_user") || "null");
    } catch {
      return null;
    }
  });

  useEffect(() => {
    if (!token) return;
    api("/api/auth/me", { token })
      .then((currentUser) => {
        localStorage.setItem("asme_user", JSON.stringify(currentUser));
        setUser(currentUser);
      })
      .catch((err) => {
        if (err.status === 401) {
          localStorage.removeItem("asme_token");
          localStorage.removeItem("asme_user");
          setToken("");
          setUser(null);
        }
      });
  }, [token]);

  useEffect(() => {
    if (!token) return undefined;
    let timer;

    function expireSession() {
      logout();
    }

    function resetTimer() {
      localStorage.setItem(LAST_ACTIVITY_KEY, String(Date.now()));
      window.clearTimeout(timer);
      timer = window.setTimeout(expireSession, IDLE_LOGOUT_MS);
    }

    function handleVisibilityChange() {
      if (document.hidden) return;
      const lastActive = Number(localStorage.getItem(LAST_ACTIVITY_KEY) || Date.now());
      if (Date.now() - lastActive > IDLE_LOGOUT_MS) {
        expireSession();
        return;
      }
      resetTimer();
    }

    const events = ["click", "keydown", "mousemove", "scroll", "touchstart"];
    events.forEach((eventName) => window.addEventListener(eventName, resetTimer, { passive: true }));
    document.addEventListener("visibilitychange", handleVisibilityChange);
    resetTimer();

    return () => {
      window.clearTimeout(timer);
      events.forEach((eventName) => window.removeEventListener(eventName, resetTimer));
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [token]);

  function handleAuth(data) {
    localStorage.setItem("asme_token", data.token);
    localStorage.setItem("asme_user", JSON.stringify(data.user));
    localStorage.setItem(LAST_ACTIVITY_KEY, String(Date.now()));
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
    localStorage.removeItem("asme_user");
    localStorage.removeItem(LAST_ACTIVITY_KEY);
    setToken("");
    setUser(null);
  }

  if (user) {
    return <Dashboard user={user} token={token} onLogout={logout} onUser={setUser} />;
  }

  return (
    <main className="relative app-atmosphere h-screen w-screen flex flex-col overflow-hidden selection:bg-white selection:text-black shrink-0">
      <BackgroundVideo />
      <Navbar
        user={user}
        onOpenAuth={openAuth}
        onDashboard={() => openAuth("login")}
        onOpenInfo={setInfoModal}
      />
      <Hero onOpenAuth={openAuth} />
      {infoModal && (
        <InfoModal
          type={infoModal}
          onClose={() => setInfoModal(null)}
          onOpenAuth={openAuth}
        />
      )}
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
  const apiBase = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
  const url = path.startsWith("http") ? path : `${apiBase}${path}`;
  let response;
  try {
    response = await fetch(url, { ...options, headers });
  } catch (err) {
    throw new Error(
      [
        "Network request failed before the backend returned a response.",
        `Request: ${options.method || "GET"} ${url || path}`,
        `Configured API base: ${apiBase || "(empty, using same domain)"}`,
        `Frontend origin: ${window.location.origin}`,
        `Backend health URL: ${(apiBase || window.location.origin).replace(/\/$/, "")}/api/health`,
        `Browser error: ${err.message}`,
        "Likely causes: wrong VITE_API_BASE_URL, backend is down/asleep, HTTPS/CORS is blocked, or Render CORS_ORIGINS does not include this exact frontend URL.",
      ].join("\n")
    );
  }

  const responseText = await response.text();
  let data = {};
  try {
    data = responseText ? JSON.parse(responseText) : {};
  } catch {
    data = { detail: responseText };
  }

  if (!response.ok) {
    const backendDetail = formatBackendDetail(data.detail);
    const error = new Error(
      [
        `Backend returned HTTP ${response.status} ${response.statusText}.`,
        `Request: ${options.method || "GET"} ${url || path}`,
        backendDetail ? `Backend detail:\n${backendDetail}` : null,
        responseText && !data.detail ? `Response body: ${responseText.slice(0, 600)}` : null,
      ]
        .filter(Boolean)
        .join("\n")
    );
    error.status = response.status;
    error.data = data;
    throw error;
  }
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
