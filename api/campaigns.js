let campaigns = [
  {
    id: 1,
    project: "Monad",
    type: "Testnet",
    tagClass: "bg-purple-950 text-purple-300 border-purple-800",
    status: "Active Farming",
    statusClass: "text-emerald-400",
    task: "Daily Faucet, Swaps & Discord Roles",
    score: "Tier S",
    estVal: 1500,
    url: "https://testnet.monad.xyz"
  },
  {
    id: 2,
    project: "Berachain V2",
    type: "Testnet",
    tagClass: "bg-amber-950 text-amber-300 border-amber-800",
    status: "Final Phase",
    statusClass: "text-amber-400",
    task: "BGT Liquidity Farming, Kodiak DEX",
    score: "Tier S",
    estVal: 2000,
    url: "https://artio.faucet.berachain.com"
  }
];

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') return res.status(200).end();

  if (req.method === 'GET') {
    return res.status(200).json({ success: true, data: campaigns });
  }

  if (req.method === 'POST') {
    const authHeader = req.headers['authorization'];
    const SECRET = process.env.BOT_SECRET || 'alpha_secret_key_123';

    if (authHeader !== `Bearer ${SECRET}`) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    const newCampaign = req.body;
    if (!newCampaign || !newCampaign.project) {
      return res.status(400).json({ error: 'Invalid payload' });
    }

    newCampaign.id = Date.now();
    campaigns.unshift(newCampaign);
    return res.status(200).json({ success: true, added: newCampaign });
  }

  return res.status(405).json({ error: 'Method Not Allowed' });
}
