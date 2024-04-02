import { injectSpeedInsights } from '@vercel/speed-insights';
import { inject } from "@vercel/analytics"

injectSpeedInsights();
inject();