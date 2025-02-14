terraform { 
  cloud { 
    organization = "photo-ranking-app" 

    workspaces { 
      tags = ["dev", "prod"]
    } 
  } 
}