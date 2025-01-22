import DiveSpotCard from "@/components/DiveSpotCard";
import { Input } from "@/components/ui/input";
import { DiveSite } from "@/types";
import { FaSearch } from "react-icons/fa";
import { NextPage } from "next";
import { redirect } from "next/navigation";
import { createClient } from "@/supabase/server";

interface SearchProps {
  searchParams: Promise<{
    q?: string;
    animal?: string;
    region?: string;
    category?: string;
  }>;
}

const SearchPage: NextPage<SearchProps> = async ({ searchParams }) => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { q, animal, region, category } = await searchParams;

  const filteredSites: DiveSite[] = region
    ? await fetch(
        `${apiUrl}/recommendations/recommend_dive_regions/${user?.id}/${region}`
      ).then((res) => res.json())
    : (q || animal || category) && !region
    ? await fetch(
        `${apiUrl}/dive-sites/search?${q ? `q=${q}` : ""}${
          animal ? `&animal=${animal}` : ""
        }${region ? `&region=${region}` : ""}
        ${category ? `&category=${category}` : ""}`
      ).then((res) => res.json())
    : [];

  const handleSubmit = async (data: FormData) => {
    "use server";
    const search = data.get("search") as string;
    redirect(`/search?q=${search}`);
  };

  return (
    <>
      <form className="flex items-center mb-10 gap-4" action={handleSubmit}>
        <Input
          type="search"
          name="search"
          placeholder="Search for dive sites, animals, regions or categories..."
          className="rounded-full text-5xl p-10"
          defaultValue={q}
          required
        />
        <button
          className="bg-black h-full aspect-square rounded-full flex items-center justify-center border hover:opacity-75 transition"
          type="submit"
        >
          <FaSearch size={40} />
        </button>
      </form>
      <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {filteredSites.length === 0 && q && (
          <p className="col-span-full text-center text-lg">
            {`No results found for ${q}`}
          </p>
        )}
        {filteredSites.map((item) => (
          <DiveSpotCard key={item.id} data={item} />
        ))}
      </section>
    </>
  );
};

export default SearchPage;
