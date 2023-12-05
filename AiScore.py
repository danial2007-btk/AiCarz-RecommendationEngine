class AIScoreInput:
    def __init__(self, total_likes, total_dislikes, total_favorites, total_time_displayed, total_ad_displays,last_ai_score):
        self.total_likes = total_likes
        self.total_dislikes = total_dislikes
        self.total_favorites = total_favorites
        self.total_time_displayed = total_time_displayed
        self.total_ad_displays = total_ad_displays
        self.last_ai_score = last_ai_score

class AIScoreCalculator:
    def __init__(self, weight1=0.2, weight2=0.2, weight3=0.6):
        self.weight1 = weight1
        self.weight2 = weight2
        self.weight3 = weight3
        # self.default_score = default_score

    def calculate_score_ratios(self, total_likes, total_dislikes, total_favorites, total_time_displayed, total_ad_displays):

        # Check if total_ad_displays is zero
        if total_ad_displays == 0:
         return 0, 0, 0, 0

        best_time = 180000
        score1 = total_likes / total_ad_displays
        score2 = total_dislikes / total_ad_displays
        score3 = total_favorites / total_ad_displays
        score4 = total_time_displayed / best_time
        return score1, score2, score3, score4

    def calculate_ai_score(self, aiscore_input):
        score1, score2, score3, score4 = self.calculate_score_ratios(
            aiscore_input.total_likes, aiscore_input.total_dislikes,
            aiscore_input.total_favorites, aiscore_input.total_time_displayed,
            aiscore_input.total_ad_displays
        )

        calculate_score = (self.weight1 * score1) - (self.weight2 * score2) + self.weight3 *(score3 * score4)
        # print("calculate Score",calculate_score)
        # print("AI Score",aiscore_input.last_ai_score)
        ai_score = aiscore_input.last_ai_score + calculate_score / 2
        return ai_score
