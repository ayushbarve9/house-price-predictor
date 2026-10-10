export function formatINR(amount) {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  const num = Number(amount);
  if (num >= 10000000) {
    return `₹${(num / 10000000).toFixed(2)} Cr`;
  } else if (num >= 100000) {
    return `₹${(num / 100000).toFixed(2)} L`;
  }
  return `₹${Math.round(num).toLocaleString('en-IN')}`;
}

export function formatFullINR(amount) {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  return `₹${Math.round(Number(amount)).toLocaleString('en-IN')}`;
}

export function getPriceTier(price) {
  if (price < 4500000) return { label: 'Affordable Housing', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' };
  if (price < 15000000) return { label: 'Mid-Segment', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20' };
  if (price < 35000000) return { label: 'Upper-Mid / Premium', color: 'bg-purple-500/10 text-purple-400 border-purple-500/20' };
  return { label: 'Ultra Luxury', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' };
}
