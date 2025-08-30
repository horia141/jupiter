"""A Message of the Day."""

from jupiter.core.domain.core.url import URL
from jupiter.core.framework.value import CompositeValue, value


@value
class MOTD(CompositeValue):
    """A Message of the Day."""

    quote: str
    author: str
    wikiquote_link: URL


MOTDs = [
    MOTD(
        quote="It is not that we have a short time to live, but that we waste a lot of it.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="The impediment to action advances action. What stands in the way becomes the way.",
        author="Marcus Aurelius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Marcus_Aurelius"),
    ),
    MOTD(
        quote="He who has a why to live can bear almost any how.",
        author="Friedrich Nietzsche",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Friedrich_Nietzsche"),
    ),
    MOTD(
        quote="Waste no more time arguing about what a good man should be. Be one.",
        author="Marcus Aurelius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Marcus_Aurelius"),
    ),
    MOTD(
        quote="Discipline equals freedom.",
        author="Jocko Willink",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Jocko_Willink"),
    ),
    MOTD(
        quote="You have power over your mind - not outside events. Realize this, and you will find strength.",
        author="Marcus Aurelius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Marcus_Aurelius"),
    ),
    MOTD(
        quote="Don't explain your philosophy. Embody it.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="How long are you going to wait before you demand the best for yourself?",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="First say to yourself what you would be; and then do what you have to do.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="You become what you give your attention to.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="The whole future lies in uncertainty: live immediately.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="No man is free, who is not master of himself.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="A man who has committed a mistake and doesn't correct it, is committing another mistake.",
        author="Confucius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Confucius"),
    ),
    MOTD(
        quote="Success is not final, failure is not fatal: it is the courage to continue that counts.",
        author="Winston Churchill",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Winston_Churchill"),
    ),
    MOTD(
        quote="You must be the change you wish to see in the world.",
        author="Mahatma Gandhi",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Mahatma_Gandhi"),
    ),
    MOTD(
        quote="The best way to find yourself is to lose yourself in the service of others.",
        author="Mahatma Gandhi",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Mahatma_Gandhi"),
    ),
    MOTD(
        quote="He who opens a school door, closes a prison.",
        author="Victor Hugo",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Victor_Hugo"),
    ),
    MOTD(
        quote="To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.",
        author="Ralph Waldo Emerson",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Ralph_Waldo_Emerson"),
    ),
    MOTD(
        quote="Do not go where the path may lead, go instead where there is no path and leave a trail.",
        author="Ralph Waldo Emerson",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Ralph_Waldo_Emerson"),
    ),
    MOTD(
        quote="Be not afraid of going slowly, be afraid only of standing still.",
        author="Chinese Proverb",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Chinese_proverbs"),
    ),
    MOTD(
        quote="The journey of a thousand miles begins with one step.",
        author="Laozi",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Laozi"),
    ),
    MOTD(
        quote="Do every act of your life as though it were the very last act of your life.",
        author="Marcus Aurelius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Marcus_Aurelius"),
    ),
    MOTD(
        quote="Dwell on the beauty of life. Watch the stars, and see yourself running with them.",
        author="Marcus Aurelius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Marcus_Aurelius"),
    ),
    MOTD(
        quote="The more we value things outside our control, the less control we have.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="Don't seek for everything to happen as you wish it would, but rather wish that everything happens as it actually will—then your life will flow well.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="Difficulties strengthen the mind, as labor does the body.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="It does not matter what you bear, but how you bear it.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="No man was ever wise by chance.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="He who angers you conquers you.",
        author="Elizabeth Kenny",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Elizabeth_Kenny"),
    ),
    MOTD(
        quote="Our life is what our thoughts make it.",
        author="Marcus Aurelius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Marcus_Aurelius"),
    ),
    MOTD(
        quote="Be tolerant with others and strict with yourself.",
        author="Marcus Aurelius",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Marcus_Aurelius"),
    ),
    MOTD(
        quote="If you want to improve, be content to be thought foolish and stupid.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="Know, first, who you are, and then adorn yourself accordingly.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="Freedom is the only worthy goal in life. It is won by disregarding things that lie beyond our control.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="It is the power of the mind to be unconquerable.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="Don't stumble over something behind you.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="To wish to be well is a part of becoming well.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="The mind that is anxious about future events is miserable.",
        author="Seneca",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Seneca_the_Younger"),
    ),
    MOTD(
        quote="Wealth consists not in having great possessions, but in having few wants.",
        author="Epictetus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epictetus"),
    ),
    MOTD(
        quote="Make the mind tougher by exposing it to adversity.",
        author="Robert Greene",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Robert_Greene"),
    ),
    MOTD(
        quote="The greater the difficulty, the more glory in surmounting it.",
        author="Epicurus",
        wikiquote_link=URL("https://en.wikiquote.org/wiki/Epicurus"),
    ),
]
