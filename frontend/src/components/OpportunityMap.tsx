import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet';
import { ExternalLink } from 'lucide-react';
import type { Match, Urgency } from '../api';

const URGENCY_COLORS: Record<Urgency, string> = {
  high: '#8C2811',
  medium: '#765208',
  low: '#1F643C',
};

const URGENCY_LEGEND: { key: Urgency; label: string }[] = [
  { key: 'high', label: 'High urgency' },
  { key: 'medium', label: 'Medium urgency' },
  { key: 'low', label: 'Low urgency' },
];

function markerIcon(match: Match, rank?: number) {
  const color = URGENCY_COLORS[match.urgency];

  if (rank) {
    return L.divIcon({
      className: '',
      html: `<div style="
          background:${color};
          color:#fff;
          width:30px;
          height:30px;
          border-radius:9999px;
          display:flex;
          align-items:center;
          justify-content:center;
          font:800 13px Inter, ui-sans-serif, sans-serif;
          border:2.5px solid white;
          box-shadow:0 3px 8px rgba(0,0,0,0.4);
        ">${rank}</div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15],
      popupAnchor: [0, -15],
    });
  }

  return L.divIcon({
    className: '',
    html: `<div style="
        background:${color};
        width:14px;
        height:14px;
        border-radius:9999px;
        border:2px solid white;
        box-shadow:0 2px 5px rgba(0,0,0,0.35);
      "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    popupAnchor: [0, -7],
  });
}

interface OpportunityMapProps {
  topMatches: Match[];
  additionalMatches: Match[];
}

const SF_CENTER: [number, number] = [37.7699, -122.4384];

export function OpportunityMap({ topMatches, additionalMatches }: OpportunityMapProps) {
  const allMatches = [...topMatches, ...additionalMatches];

  return (
    <section className="card-panel overflow-hidden p-0" aria-labelledby="opportunity-map-heading">
      <div className="flex flex-col gap-3 border-b border-line/70 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <h2 className="font-display text-2xl font-semibold text-ink" id="opportunity-map-heading">
            Where you can help
          </h2>
          <p className="mt-1 text-sm text-muted">Tap a pin to see the time commitment and visit the organization.</p>
        </div>
        <ul className="flex shrink-0 flex-wrap gap-x-4 gap-y-1.5" aria-label="Map pin urgency legend">
          {URGENCY_LEGEND.map(({ key, label }) => (
            <li className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted" key={key}>
              <span className="inline-block size-2.5 rounded-full border border-white shadow-sm" style={{ background: URGENCY_COLORS[key] }} aria-hidden="true" />
              {label}
            </li>
          ))}
        </ul>
      </div>
      <div className="h-[190px] w-full sm:h-[220px]">
        <MapContainer center={SF_CENTER} zoom={12} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {allMatches.map((match, index) => {
            const rank = index < topMatches.length ? index + 1 : undefined;
            return (
              <Marker key={match.opportunity_id} position={[match.lat, match.lng]} icon={markerIcon(match, rank)}>
                <Popup>
                  <div className="min-w-[190px]">
                    <p className="text-sm font-bold text-ink">{match.org_name}</p>
                    <p className="text-sm text-muted">{match.title}</p>
                    <p className="mt-1.5 text-xs text-muted">{match.neighborhood} · {match.commitment}</p>
                    <p className="mt-1 text-xs font-semibold text-primary">
                      {Math.round(match.score * 100)}% match · {match.urgency} urgency
                    </p>
                    {match.org_url && (
                      <a
                        className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-primary underline-offset-2 hover:underline"
                        href={match.org_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Visit website
                        <ExternalLink className="size-3" aria-hidden="true" />
                      </a>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </section>
  );
}
