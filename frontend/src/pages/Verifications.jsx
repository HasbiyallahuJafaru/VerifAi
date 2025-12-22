import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { CheckCircle2, ExternalLink, Link as LinkIcon, ShieldCheck, MapPin } from 'lucide-react'

function Verifications() {
  return (
    <div className="max-w-5xl mx-auto space-y-8 text-slate-50">
      <div className="bg-white/10 backdrop-blur-xl rounded-xl p-6 border border-white/15 shadow-lg">
        <h2 className="text-2xl font-bold text-white">Initiate Verification</h2>
        <p className="text-slate-200 mt-2">
          Admins generate and send verification links. Customers complete verification at /verify using their unique link.
        </p>
      </div>

      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <ShieldCheck className="w-5 h-5 text-blue-600" />
            How it works
          </CardTitle>
          <CardDescription>Use this flow to start a new verification for a customer.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border border-white/50 bg-white/80 backdrop-blur-xl p-4">
              <p className="text-sm font-semibold text-slate-900 mb-2">Step 1 — Create link</p>
              <p className="text-sm text-slate-700">Open Generate Link, enter the customer details, and create a one-time verification URL.</p>
            </div>
            <div className="rounded-lg border border-white/50 bg-white/80 backdrop-blur-xl p-4">
              <p className="text-sm font-semibold text-slate-900 mb-2">Step 2 — Send to customer</p>
              <p className="text-sm text-slate-700">Share the generated link with the customer (email/SMS). They will complete verification at /verify.</p>
            </div>
            <div className="rounded-lg border border-white/50 bg-white/80 backdrop-blur-xl p-4">
              <p className="text-sm font-semibold text-slate-900 mb-2">Step 3 — Track status</p>
              <p className="text-sm text-slate-700">View results in the dashboard once the customer submits. Links expire after 24 hours and are single-use.</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button asChild className="gap-2">
              <Link to="/dashboard/generate-link">
                <LinkIcon className="w-4 h-4" />
                Generate Link
              </Link>
            </Button>
            <Button asChild variant="outline" className="gap-2">
              <Link to="/verify" target="_blank" rel="noreferrer">
                <ExternalLink className="w-4 h-4" />
                Preview Customer View
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <MapPin className="w-5 h-5 text-blue-600" />
            What the customer sees
          </CardTitle>
          <CardDescription>Customers only interact with the public verification page at /verify using their unique token.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm text-gray-700">
          <ul className="space-y-2">
            <li className="flex items-start gap-2"><CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" /> Secure, single-use token embedded in the link</li>
            <li className="flex items-start gap-2"><CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" /> Customer consents and shares location to verify address</li>
            <li className="flex items-start gap-2"><CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" /> We compare device location to the provided address and compute risk</li>
            <li className="flex items-start gap-2"><CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" /> Results are posted back to your dashboard/API</li>
          </ul>
          <Separator />
          <p className="text-xs text-gray-500">
            Reminder: Admins should never complete verifications on behalf of customers. Always send the generated link.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default Verifications