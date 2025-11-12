import { trpc } from "@/lib/trpc";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Loader2, Plus, Edit2, Trash2, Search } from "lucide-react";
import { toast } from "sonner";

interface CategoryFormData {
  name: string;
  description: string;
  imageFileName: string;
  parentId?: number;
  isActive: number;
}

export default function CategoriesDashboard() {
  const { user, isAuthenticated } = useAuth();
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "id" | "createdAt">("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<any>(null);
  const [formData, setFormData] = useState<CategoryFormData>({
    name: "",
    description: "",
    imageFileName: "",
    isActive: 1,
  });

  const utils = trpc.useUtils();

  // Fetch categories
  const { data: categoriesData, isLoading } = trpc.categories.list.useQuery({
    skip: page * 10,
    take: 10,
    search,
    sortBy,
    sortOrder,
  });

  // Fetch root categories for parent selection
  const { data: rootCategories } = trpc.categories.getRoots.useQuery();

  // Mutations
  const createMutation = trpc.categories.create.useMutation({
    onSuccess: () => {
      utils.categories.list.invalidate();
      setIsCreateOpen(false);
      setFormData({
        name: "",
        description: "",
        imageFileName: "",
        isActive: 1,
      });
      toast.success("Categoria criada com sucesso!");
    },
    onError: (error) => {
      toast.error(`Erro ao criar categoria: ${error.message}`);
    },
  });

  const updateMutation = trpc.categories.update.useMutation({
    onSuccess: () => {
      utils.categories.list.invalidate();
      setIsEditOpen(false);
      setSelectedCategory(null);
      setFormData({
        name: "",
        description: "",
        imageFileName: "",
        isActive: 1,
      });
      toast.success("Categoria atualizada com sucesso!");
    },
    onError: (error) => {
      toast.error(`Erro ao atualizar categoria: ${error.message}`);
    },
  });

  const deleteMutation = trpc.categories.delete.useMutation({
    onSuccess: () => {
      utils.categories.list.invalidate();
      toast.success("Categoria deletada com sucesso!");
    },
    onError: (error) => {
      toast.error(`Erro ao deletar categoria: ${error.message}`);
    },
  });
