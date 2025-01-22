import { DiveSite } from "@/types";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./ui/carousel";
import TallDiveSiteCard from "./TallDiveSiteCard";

interface TopTenSectionProps {
  title: string;
  apiUrl: string;
}

const TopTenSection: React.FC<TopTenSectionProps> = async ({
  title,
  apiUrl,
}) => {
  const data: DiveSite[] = await fetch(apiUrl).then((res) => res.json());

  return (
    <div className="flex flex-col gap-2">
      <h2 className="font-bold text-2xl">{title}</h2>
      <Carousel className="w-full">
        <CarouselContent className="-ml-1 py-2 pr-4">
          {data.slice(0, 9).map((item, index) => (
            <CarouselItem
              key={index}
              className="pl-4 basis-full md:basis-1/2 lg:basis-1/3 xl:basis-1/3 2xl:basis-1/4"
            >
              <div className="p-1 flex items-center">
                <p className="drop-shadow-[0_1.2px_1.8px_rgba(255,255,255,0.8)] text-black text-[200px] font-bold select-none">
                  {index + 1}
                </p>
                <TallDiveSiteCard data={item} />
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
};

export default TopTenSection;
