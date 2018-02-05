package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/crypto/sha3"
	"github.com/gin-gonic/gin"
)

type PendingTx struct {
	RawTx          string
	TxHash         string
	SubmissionTime int64
}

type Server struct {
	router     *gin.Engine
	pendingTxs *[]PendingTx
	shakeHash  sha3.ShakeHash
}

func (s Server) getTime() int64 {
	realTime := time.Now().Unix() * 1000

	resp, err := http.Get("http://scheduler:7000/get")
	if err != nil {
		return realTime
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return realTime
	}

	var d struct {
		Timestamp int64 `json:"timestamp"`
	}
	err = json.Unmarshal(body, &d)
	return d.Timestamp
}

func (s Server) sendRawTransaction(rawTx string) string {
	txHash := crypto.Keccak256Hash(common.FromHex(rawTx)).Hex()
	currentTime := s.getTime()
	*s.pendingTxs = append(*s.pendingTxs, PendingTx{rawTx, txHash, currentTime})
	return txHash
}

func callBlockchain(methodName, params, rpcVersion, id interface{}) []byte {
	url := "http://blockchain:8545/jsonrpc"
	payload := map[string]interface{}{
		"method":  methodName,
		"params":  params,
		"jsonrpc": rpcVersion,
		"id":      id,
	}
	payloadJSON, err := json.Marshal(payload)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(payloadJSON))
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	return body
}

func (s Server) checkPendingTxs() {
	currentTime := s.getTime()
	nonExpiredTxs := &[]PendingTx{}
	for _, tx := range *s.pendingTxs {
		if tx.SubmissionTime+5000 <= currentTime {
			params := []string{tx.RawTx}
			response := callBlockchain("eth_sendRawTransaction", params, "2.0", "1")

			var jsonResp map[string]interface{}
			json.Unmarshal(response, &jsonResp)
			log.Printf("pending response: %v", jsonResp)
		} else {
			*nonExpiredTxs = append(*nonExpiredTxs, tx)
		}
	}
	*s.pendingTxs = *nonExpiredTxs
}

func (s Server) index(c *gin.Context) {
	s.checkPendingTxs()

	var data map[string]interface{}
	err := c.ShouldBindJSON(&data)
	if err != nil {
		log.Println("malformed data")
	}

	methodName := data["method"]
	params := data["params"]
	rpcVersion := data["jsonrpc"]
	id := data["id"]

	switch methodName {
	case "eth_sendTransaction":
		c.JSON(
			http.StatusOK,
			gin.H{
				"id":      id,
				"jsonrpc": rpcVersion,
				"result":  "unsupported command in delay mode",
			})
	case "eth_getTransactionByHash":
		response := callBlockchain(methodName, params, rpcVersion, id)
		var jsonResp map[string]interface{}
		json.Unmarshal(response, &jsonResp)
		if jsonResp["result"] != nil {
			c.JSON(
				http.StatusOK,
				jsonResp,
			)
		}

		tmp := params.([]interface{})
		txh := tmp[0].(string)
		for _, tx := range *s.pendingTxs {
			if tx.TxHash == txh {
				c.JSON(
					http.StatusOK,
					gin.H{
						"id":      id,
						"jsonrpc": rpcVersion,
						"result": map[string]string{
							"hash": txh,
						},
					})
			}
		}

		c.JSON(
			http.StatusOK,
			gin.H{
				"id":      id,
				"jsonrpc": rpcVersion,
				"result":  nil,
			})
	case "eth_sendRawTransaction":
		tmp := params.([]interface{})
		rawTx := tmp[0].(string)
		txh := s.sendRawTransaction(rawTx)
		c.JSON(
			http.StatusOK,
			gin.H{
				"id":      id,
				"jsonrpc": rpcVersion,
				"result":  txh,
			})
	default:
		response := callBlockchain(methodName, params, rpcVersion, id)
		var jsonResp map[string]interface{}
		json.Unmarshal(response, &jsonResp)
		c.JSON(
			http.StatusOK,
			jsonResp,
		)
	}
}

func New() *Server {
	router := gin.Default()
	pendingTxs := &[]PendingTx{}
	h := sha3.NewShake256()
	return &Server{router, pendingTxs, h}
}

func (s Server) Start() {
	s.router.POST("/", s.index)
	s.router.Run(":8540")
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	server := New()
	server.Start()
}
