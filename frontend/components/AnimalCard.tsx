import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { AnimalRecommendation } from "@/types";
import Image from "next/image";
import Link from "next/link";
import React from "react";

interface AnimalCardProps {
  data: AnimalRecommendation;
}

const AnimalCard: React.FC<AnimalCardProps> = ({ data }) => {
  return (
    <Card className="relative hover:scale-105 transition overflow-hidden hover:border-white hover:border-2 border-opacity-0 hover:border-opacity-100 shadow-xl duration-300 aspect-square select-none rounded-3xl">
      <Link
        href={`/search?animal=${data.animal_name}`}
        className="transition flex flex-col justify-between h-full"
      >
        <Image
          src={data.animal_image_url}
          width={500}
          height={500}
          alt="Picture of the author"
          className="rounded-t-md object-cover h-full w-full"
          priority
        />
        <CardHeader
          className="bg-zinc-800 absolute bottom-0 left-0 right-0 h-2/3 flex justify-end items-center"
          style={{
            background:
              "linear-gradient(to bottom, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.75) 100%)",
          }}
        >
          <CardTitle className="text-sm sm:text-lg md:text-xl xl:text-3xl">
            {data.animal_name}
          </CardTitle>
          {/* <CardDescription>Description</CardDescription> */}
        </CardHeader>
        {/* <CardContent></CardContent> */}
        {/* <CardFooter className="flex justify-end">
          <Button>Explore</Button>
        </CardFooter> */}
      </Link>
    </Card>
  );
};

export default AnimalCard;
