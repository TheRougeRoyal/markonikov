import uuid
from datetime import datetime, timezone
import database
import markovify

SAMPLE_MODELS = [
    {
        "name": "Classic Literature",
        "text": """It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair, we had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct the other way.

To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer the slings and arrows of outrageous fortune, or to take arms against a sea of troubles, and by opposing end them. To die: to sleep; no more; and by a sleep to say we end the heart-ache and the thousand natural shocks that flesh is heir to.

All happy families are alike; each unhappy family is unhappy in its own way. Everything was in confusion in the Oblonskys' house. The wife had discovered that the husband was carrying on an intrigue with a French girl, who had been a governess in their family, and she had announced to her husband that she could not go on living in the same house with him.

It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered as the rightful property of some one or other of their daughters.

Last night I dreamt I went to Manderley again. It seemed to me that I was driven up the narrow winding drive with the tall trees on either side. The drive was little more than a cart-track, and bordered on either side by rough pasture, and the wheel bumped and swayed over the uneven ground.

Call me Ishmael. Some years ago, never mind how long precisely, having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen, and regulating the circulation.

In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters. And God said, Let there be light: and there was light. And God saw the light, that it was good: and God divided the light from the darkness.

It was a bright cold day in April, and the clocks were striking thirteen. Winston Smith, his chin nuzzled into his breast in an effort to escape the vile wind, slipped quickly through the glass doors of Victory Mansions, though not quickly enough to prevent a swirl of gritty dust from entering along with him.

Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense.""",
        "state_size": 2,
    },
    {
        "name": "Science & Technology",
        "text": """Artificial intelligence is transforming every aspect of our lives, from how we communicate to how we work and play. Machine learning algorithms can now recognize images, translate languages, and even compose music with startling accuracy.

Quantum computing represents a fundamental shift in computational power. By harnessing the principles of quantum mechanics, these machines can solve problems that would take classical computers billions of years to complete.

The internet has connected billions of people across the globe, enabling instant communication and access to the sum of human knowledge. Social media platforms have revolutionized how we share information and maintain relationships.

DNA sequencing has become dramatically cheaper and faster over the past decade, opening up new possibilities in personalized medicine and genetic engineering. CRISPR technology allows scientists to edit genes with unprecedented precision.

Renewable energy sources like solar and wind power are becoming increasingly cost-competitive with fossil fuels. Battery technology is advancing rapidly, making electric vehicles practical for everyday use.

Blockchain technology has introduced new possibilities for decentralized systems, from cryptocurrency to supply chain management. Smart contracts can automatically execute agreements when predetermined conditions are met.

Climate change poses one of the greatest challenges facing humanity today. Rising global temperatures are causing more frequent extreme weather events, melting polar ice caps, and threatening biodiversity across the planet.

Space exploration has entered a new era with private companies joining government agencies in the quest to explore the cosmos. Mars colonization, asteroid mining, and space tourism are no longer confined to science fiction.

The human brain contains approximately 86 billion neurons, each connected to thousands of others through trillions of synapses. Understanding how these connections give rise to consciousness remains one of the greatest scientific mysteries.

Nanotechnology operates at the scale of atoms and molecules, enabling the creation of materials and devices with remarkable properties. From targeted drug delivery to ultra-strong materials, the applications are virtually limitless.""",
        "state_size": 2,
    },
    {
        "name": "Philosophy & Wisdom",
        "text": """The unexamined life is not worth living. Knowledge is knowing that a tomato is a fruit; wisdom is not putting it in a fruit salad. The only true wisdom is in knowing you know nothing.

In the middle of difficulty lies opportunity. Life is what happens when you are busy making other plans. The journey of a thousand miles begins with a single step.

We are what we repeatedly do. Excellence, then, is not an act, but a habit. It is not that we have a short time to live, but that we waste a great deal of it.

The greatest glory in living lies not in never falling, but in rising every time we fall. Success is not final, failure is not fatal: it is the courage to continue that counts.

To think is to differ. The mind is not a vessel to be filled, but a fire to be kindled. Education is not the learning of facts, but the training of the mind to think.

Happiness depends upon ourselves. Happiness is not something ready-made. It comes from your own actions. The purpose of our lives is to be happy.

Be the change that you wish to see in the world. Actions speak louder than words. The best time to plant a tree was twenty years ago. The second best time is now.

In three words I can sum up everything I have learned about life: it goes on. Life is really simple, but we insist on making it complicated. The older I get, the more I realize that it is not about winning or losing, but about living.

The only thing I know is that I know nothing. I think, therefore I am. To be is to be perceived. The mind的一切depends on the body, but the body depends on nothing.

Where there is love there is life. Love is composed of a single soul inhabiting two bodies. The course of true love never did run smooth.""",
        "state_size": 2,
    },
]


def seed_models():
    if database.model_count() > 0:
        return

    for sample in SAMPLE_MODELS:
        try:
            model = markovify.Text(sample["text"], state_size=sample["state_size"])
            model_id = str(uuid.uuid4())
            model_json = model.to_json()
            created_at = datetime.now(timezone.utc).isoformat()
            preview = sample["text"][:200]
            database.save_model_to_db(
                model_id, model_json, sample["state_size"], False, created_at,
                training_text_preview=preview,
            )
            print(f"[seed] Created model: {sample['name']} ({model_id[:8]}...)")
        except Exception as e:
            print(f"[seed] Failed to create {sample['name']}: {e}")
