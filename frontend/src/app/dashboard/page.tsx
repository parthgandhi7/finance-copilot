import { DocumentList } from "@/components/dashboard/document-list";
import { Card } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Financial Dashboard</h1>
        <p className="text-muted-foreground">Monitor uploads, processing status, and assistant highlights.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-5"><p className="text-sm text-muted-foreground">Monthly Net Cashflow</p><p className="mt-2 text-2xl font-semibold">+$12,480</p></Card>
        <Card className="p-5"><p className="text-sm text-muted-foreground">Expense Alerts</p><p className="mt-2 text-2xl font-semibold">3</p></Card>
        <Card className="p-5"><p className="text-sm text-muted-foreground">Docs Processed</p><p className="mt-2 text-2xl font-semibold">18</p></Card>
      </div>
      <DocumentList />
    </section>
  );
}
