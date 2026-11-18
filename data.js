/* Data catalog — 9 local demo clips (3 Gaming, 3 Learning, 3 Sports), each under 5 minutes.
   To add or swap a video: drop the .mp4 into /media, (optionally) a thumbnail into /media/thumbs,
   then add/edit an entry in VIDEO_SOURCES below. Keep clips <= 5:00. */
const VIDEO_SOURCES = [
  {
    "title": "Pong AI vs AI — Non-Stop Rally Match",
    "category": "Gaming",
    "url": "./media/gaming-pong.mp4",
    "poster": "./media/thumbs/gaming-pong.jpg",
    "duration": "2:00"
  },
  {
    "title": "Snake Bot Plays Itself — How Long Can It Get?",
    "category": "Gaming",
    "url": "./media/gaming-snake.mp4",
    "poster": "./media/thumbs/gaming-snake.jpg",
    "duration": "2:00"
  },
  {
    "title": "Breakout Auto-Play — Brick Smashing Session",
    "category": "Gaming",
    "url": "./media/gaming-breakout.mp4",
    "poster": "./media/thumbs/gaming-breakout.jpg",
    "duration": "1:30"
  },
  {
    "title": "Learn Multiplication Tables 2–9 the Visual Way",
    "category": "Learning",
    "url": "./media/learning-times-tables.mp4",
    "poster": "./media/thumbs/learning-times-tables.jpg",
    "duration": "0:56"
  },
  {
    "title": "The Pythagorean Theorem Explained with Squares",
    "category": "Learning",
    "url": "./media/learning-pythagoras.mp4",
    "poster": "./media/thumbs/learning-pythagoras.jpg",
    "duration": "1:00"
  },
  {
    "title": "Counting in Binary — Bits & Bytes for Beginners",
    "category": "Learning",
    "url": "./media/learning-binary.mp4",
    "poster": "./media/thumbs/learning-binary.jpg",
    "duration": "0:50"
  },
  {
    "title": "Free Throw Practice — Swish or Rim Out?",
    "category": "Sports",
    "url": "./media/sports-basketball.mp4",
    "poster": "./media/thumbs/sports-basketball.jpg",
    "duration": "1:40"
  },
  {
    "title": "100m Dash Heats — Who Takes Gold?",
    "category": "Sports",
    "url": "./media/sports-sprint.mp4",
    "poster": "./media/thumbs/sports-sprint.jpg",
    "duration": "1:20"
  },
  {
    "title": "Penalty Shootout — Goals vs Saves",
    "category": "Sports",
    "url": "./media/sports-penalty.mp4",
    "poster": "./media/thumbs/sports-penalty.jpg",
    "duration": "1:28"
  }
];

const CATEGORY_NAMES = ["All", "Gaming", "Learning", "Sports", "Recently uploaded", "Watched"];
const REAL_CATEGORIES = ["Gaming", "Learning", "Sports"];

const CHANNELS_BY_CATEGORY = {
  Gaming: ["Pixel House", "Next Level", "Arcade Bytes", "Retro Realm"],
  Learning: ["Study Hub", "Discovery Zone", "Quick Lessons", "The Daily Edit"],
  Sports: ["Game Day", "Sports Central", "Top Plays", "Trending Now"]
};

/* How many cards to generate per category (cycles through that category's clips). */
const CATEGORY_VIDEO_COUNTS = 60;

const VIDEOS_BY_CATEGORY = Object.fromEntries(REAL_CATEGORIES.map(category => {
  const sources = VIDEO_SOURCES.filter(v => v.category === category);
  const channels = CHANNELS_BY_CATEGORY[category];
  const items = Array.from({ length: CATEGORY_VIDEO_COUNTS }, (_, index) => {
    const source = sources[index % sources.length];
    const round = Math.floor(index / sources.length);
    const sourceIndex = VIDEO_SOURCES.indexOf(source);
    return {
      id: `${category.toLowerCase()}-${index + 1}`,
      category,
      title: round === 0 ? source.title : `${source.title} (Part ${round + 1})`,
      channel: channels[(index * 3 + sourceIndex) % channels.length],
      views: `${1 + (index * 7) % 97}K views`,
      age: `${1 + (index * 5) % 30} days ago`,
      duration: source.duration,
      videoUrl: source.url,
      thumbnail: source.poster,
      channelAvatar: `https://i.pravatar.cc/80?img=${(index + sourceIndex) % 70 + 1}`,
      description: `${category} demo clip for this YouTube-style interface.`
    };
  });
  return [category, items];
}));

/* Interleave categories so the "All" feed mixes Gaming / Learning / Sports. */
const ALL_VIDEOS = (() => {
  const lists = REAL_CATEGORIES.map(c => VIDEOS_BY_CATEGORY[c]);
  const mixed = [];
  for (let i = 0; i < CATEGORY_VIDEO_COUNTS; i++) lists.forEach(l => mixed.push(l[i]));
  return mixed;
})();
