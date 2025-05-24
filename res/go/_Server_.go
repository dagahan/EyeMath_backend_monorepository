package main



type Client struct {
	Email string
	Password string
	FirstName string
	LastName string
	Token string
}


var database = map[string]ClientProfile{
	"user1": {
		Email: "nikitosu27@gmail.com",
		Password: "nikitosu27",
		FirstName: "Nikita",
		LastName: "Usov",
		Token: "0"
	},
	"user2": {
		Email: "AlexJira3@gmail.com",
		Password: "223567",
		FirstName: "Alex",
		LastName: "Jira",
		Token: "1"
	}
}