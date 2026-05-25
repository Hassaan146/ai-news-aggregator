# AI News Aggregator

A curated list of websites that regularly publish AI news, product updates, research, policy, and industry analysis. Use these as seed sources for tracking OpenAI news and the broader AI ecosystem.

Last updated: May 24, 2026

## Official AI Company News

- https://openai.com/news/
- https://openai.com/blog/
- https://www.anthropic.com/news
- https://deepmind.google/blog/
- https://ai.googleblog.com/
- https://cloud.google.com/blog/products/ai-machine-learning
- https://ai.meta.com/blog/
- https://blogs.microsoft.com/ai/
- https://www.microsoft.com/en-us/research/research-area/artificial-intelligence/
- https://blogs.nvidia.com/blog/category/deep-learning/
- https://mistral.ai/news/
- https://x.ai/news
- https://huggingface.co/blog
- https://stability.ai/news
- https://cohere.com/blog
- https://www.perplexity.ai/hub/blog
- https://aws.amazon.com/blogs/machine-learning/
- https://machinelearning.apple.com/

## AI News And Tech Media

- https://techcrunch.com/category/artificial-intelligence/
- https://www.theverge.com/ai-artificial-intelligence
- https://venturebeat.com/category/ai/
- https://www.technologyreview.com/topic/artificial-intelligence/
- https://www.wired.com/tag/artificial-intelligence/
- https://arstechnica.com/tag/artificial-intelligence/
- https://www.axios.com/technology/artificial-intelligence
- https://www.cnbc.com/artificial-intelligence/
- https://the-decoder.com/
- https://www.unite.ai/
- https://www.artificialintelligence-news.com/
- https://aibusiness.com/
- https://www.infoq.com/ai-ml-data-eng/
- https://www.kdnuggets.com/
- https://www.analyticsvidhya.com/blog/
- https://towardsdatascience.com/
- https://www.marktechpost.com/
- https://syncedreview.com/

## Research And Model Tracking

- https://arxiv.org/list/cs.AI/recent
- https://arxiv.org/list/cs.LG/recent
- https://arxiv.org/list/cs.CL/recent
- https://paperswithcode.com/
- https://huggingface.co/papers
- https://hai.stanford.edu/news
- https://bair.berkeley.edu/blog/
- https://www.csail.mit.edu/news
- https://thegradient.pub/
- https://distill.pub/
- https://research.google/blog/
- https://allenai.org/blog

## Newsletters And Curated Feeds

- https://www.deeplearning.ai/the-batch/
- https://jack-clark.net/
- https://lastweekin.ai/
- https://www.bensbites.co/
- https://tldr.tech/ai
- https://futuretools.io/news
- https://www.ai-roundup.dev/
- https://theoutpost.ai/
- https://aiagentic.news/

## AI Policy, Safety, And Society

- https://www.nist.gov/artificial-intelligence
- https://oecd.ai/
- https://ainowinstitute.org/
- https://futureoflife.org/artificial-intelligence/
- https://www.safe.ai/
- https://partnershiponai.org/
- https://www.eff.org/issues/ai
- https://www.brookings.edu/topic/artificial-intelligence/

## Suggested Starter Sources For This Project

For a practical first version of the aggregator, start with these high-signal sources:

- https://openai.com/news/
- https://www.anthropic.com/news
- https://deepmind.google/blog/
- https://techcrunch.com/category/artificial-intelligence/
- https://www.theverge.com/ai-artificial-intelligence
- https://www.technologyreview.com/topic/artificial-intelligence/
- https://venturebeat.com/category/ai/
- https://www.deeplearning.ai/the-batch/
- https://arxiv.org/list/cs.AI/recent
- https://huggingface.co/papers

## User Accounts And Email Sending

User accounts are stored in the `users` table. Accounts must use a Gmail or
Googlemail address because the first live email sender uses Gmail SMTP.

Add these values to `.env` before sending live emails:

```env
GMAIL_ADDRESS=your_sender_gmail@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password_here
```

The Gmail app password is not your normal Gmail password. Create it from your
Google Account security settings after enabling 2-Step Verification.

Create or update a user:

```powershell
py -m app.user_runner --create --name Hassan --email your_user@gmail.com --profile default_ai_reader
```

Preview the email for a stored user:

```powershell
py -m app.email_runner --to your_user@gmail.com --hours 24 --top-n 10 --no-llm
```

Send the live email:

```powershell
py -m app.email_runner --to your_user@gmail.com --hours 24 --top-n 10 --send --no-llm
```

